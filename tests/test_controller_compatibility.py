from __future__ import annotations

import pytest

from cfdc.lab import (
    GeneratedModelEnvelopeV1,
    SessionActionError,
    StateFeedbackControllerSpec,
    bootstrap_controller_candidate,
    confirm_generated_model,
    confirm_recommended_controller,
    create_simulation_from_discovery,
    evaluate_controller_compatibility,
    run_next_trial,
)
from cfdc.lab.model_discovery import _rehash, _sha256
from cfdc.models import (
    ControllerCandidate,
    StateSpaceModelSpec,
    TransferFunctionModelSpec,
)
from tests.test_model_discovery_session import session_with_ready_result
from tests.simulation_fixtures import cartpole_model, vtol_model
from cfdc.sim import registered_run_envelope


def confirmed_pi_tf_session():
    proposed = session_with_ready_result()
    return confirm_generated_model(
        proposed,
        expected_revision=proposed.revision,
    )


def mimo_envelope() -> GeneratedModelEnvelopeV1:
    model = StateSpaceModelSpec(
        a=[[0.0, 1.0], [-2.0, -0.5]],
        b=[[1.0, 0.0], [0.0, 1.0]],
        c=[[1.0, 0.0], [0.0, 1.0]],
        d=[[0.0, 0.0], [0.0, 0.0]],
        time_domain="continuous",
        state_names=["x1", "x2"],
        input_signal_ids=["u1", "u2"],
        output_signal_ids=["y1", "y2"],
        initial_state=[0.0, 0.0],
        signal_units={
            "x1": "m",
            "x2": "m/s",
            "u1": "N",
            "u2": "N",
            "y1": "m",
            "y2": "m/s",
        },
    )
    return GeneratedModelEnvelopeV1(
        model_role="user_evidence_model",
        model=model,
        parameter_evidence=[
            {
                "parameter_path": "model.a[0][0]",
                "value": 0.0,
                "unit": "1/s",
                "source": "user_supplied",
                "source_fact_ids": ["mimo_state_space"],
            }
        ],
        assumptions=["The supplied matrices describe a local LTI model."],
        limitations=["The result is valid only for this software model."],
        plain_language_summary=(
            "Two control inputs act on two measured outputs through a "
            "two-state continuous model."
        ),
        equation_latex=[r"\dot{x}=Ax+Bu", r"y=Cx"],
        experiment_proposal={
            "initial_state": {"x1": 0.0, "x2": 0.0},
            "reference": {"y1": 0.1, "y2": 0.1},
            "horizon_s": 10.0,
            "sample_time_s": 0.02,
            "actuator_bounds": {
                "u1": [-5.0, 5.0],
                "u2": [-5.0, 5.0],
            },
            "state_bounds": {
                "x1": [-2.0, 2.0],
                "x2": [-2.0, 2.0],
            },
            "output_bounds": {
                "y1": [-2.0, 2.0],
                "y2": [-2.0, 2.0],
            },
            "signal_units": model.signal_units,
            "evidence_fact_ids": ["mimo_state_space"],
        },
    )


def confirmed_mimo_session():
    base = confirmed_pi_tf_session()
    envelope = mimo_envelope()
    payload = base.model_dump(mode="python")
    payload.update(
        {
            "pending_envelope": envelope,
            "pending_envelope_sha256": _sha256(envelope),
            "confirmed_envelope": envelope,
            "confirmed_envelope_sha256": _sha256(envelope),
        }
    )
    return _rehash(payload)


def test_pi_candidate_rebinds_to_confirmed_siso_model():
    session = confirmed_pi_tf_session()

    checked = evaluate_controller_compatibility(
        session,
        expected_revision=session.revision,
    )

    assert checked.state == "simulation_ready"
    assert checked.selected_controller.kind == "pi"
    assert checked.bound_model_sha256 == checked.confirmed_envelope_sha256
    assert checked.compatibility_result.status == "compatible"


def test_siso_pi_cannot_run_against_mimo_without_replacement_confirmation():
    session = confirmed_mimo_session()
    checked = evaluate_controller_compatibility(
        session,
        expected_revision=session.revision,
    )

    assert checked.state == "controller_replacement_review"
    assert checked.compatibility_result.status == "replacement_required"
    assert checked.recommended_controller is None
    with pytest.raises(SessionActionError, match="replacement"):
        create_simulation_from_discovery(
            checked,
            expected_revision=checked.revision,
        )


def test_controllable_user_mimo_receives_deterministic_state_feedback():
    session = confirmed_mimo_session()

    checked = evaluate_controller_compatibility(
        session,
        all_states_available=True,
        expected_revision=session.revision,
    )

    assert checked.state == "controller_replacement_review"
    assert isinstance(
        checked.recommended_controller,
        StateFeedbackControllerSpec,
    )
    assert checked.replacement_sha256
    assert "mimo_decoupling_matrix" not in checked.model_dump_json()


def test_replacement_requires_matching_hash_then_creates_simulation():
    session = confirmed_mimo_session()
    checked = evaluate_controller_compatibility(
        session,
        all_states_available=True,
        expected_revision=session.revision,
    )

    with pytest.raises(SessionActionError, match="hash"):
        confirm_recommended_controller(
            checked,
            replacement_sha256="0" * 64,
            expected_revision=checked.revision,
        )
    ready = confirm_recommended_controller(
        checked,
        replacement_sha256=checked.replacement_sha256,
        expected_revision=checked.revision,
    )
    simulation = create_simulation_from_discovery(
        ready,
        expected_revision=ready.revision,
    )

    assert ready.state == "simulation_ready"
    assert ready.selected_controller == checked.recommended_controller
    assert simulation.state == "trial_pending"
    assert simulation.confirmed_model == ready.confirmed_envelope.model
    assert simulation.source_plant_id == ready.confirmed_envelope_sha256


@pytest.mark.parametrize(
    ("architecture", "gains", "design", "expected_kind"),
    [
        ("conservative_P", {"kp": 0.0}, {}, "p"),
        (
            "filtered_PID",
            {"kp": 1.0, "ki": 0.2, "kd": 0.1},
            {"filter_cutoff_rad_s": 8.0},
            "filtered_pid",
        ),
        (
            "lead",
            {"gain": 1.0},
            {"zero_rad_s": 1.0, "pole_rad_s": 4.0},
            "lead",
        ),
        (
            "lag",
            {"gain": 1.0},
            {"zero_rad_s": 4.0, "pole_rad_s": 1.0},
            "lag",
        ),
        (
            "notch",
            {"gain": 1.0},
            {
                "center_frequency_rad_s": 5.0,
                "zero_damping_ratio": 0.1,
                "pole_damping_ratio": 0.3,
            },
            "notch",
        ),
    ],
)
def test_stage5_bootstrap_covers_all_declared_scalar_runtime_types(
    architecture,
    gains,
    design,
    expected_kind,
):
    model = TransferFunctionModelSpec(
        numerator=[1.0],
        denominator=[2.0, 1.0],
        input_signal_id="u",
        output_signal_id="y",
        input_units="V",
        output_units="m",
    )
    candidate = ControllerCandidate(
        architecture=architecture,
        gains=gains,
        design_parameters=design,
        tunable_gain_names=list(gains),
        release_level="candidate_unvalidated",
        status="ready_for_conservative_trial",
    )

    result = bootstrap_controller_candidate(candidate, model)

    assert result.status == "ready"
    assert result.controller.kind == expected_kind
    if any(value == 0.0 for value in gains.values()):
        zero_rule = next(
            rule for rule in result.tuning_profile.parameters if gains[rule.name] == 0.0
        )
        assert zero_rule.zero_step_scale is not None


def registered_envelope(model) -> GeneratedModelEnvelopeV1:
    runtime = registered_run_envelope(model)
    policy_id = (
        "registered_cartpole_five_scenario/v1"
        if model.template_id == "underactuated_cartpole"
        else "registered_vtol_five_scenario/v1"
    )
    return GeneratedModelEnvelopeV1(
        model_role="registered_nonlinear_model",
        model=model,
        parameter_evidence=[
            {
                "parameter_path": (f"model.parameters.{next(iter(model.parameters))}"),
                "value": next(iter(model.parameters.values())),
                "unit": "registered_unit",
                "source": "user_supplied",
                "source_fact_ids": ["registered_parameters"],
            }
        ],
        assumptions=["Use the closed registered nonlinear runtime."],
        limitations=["This is a software-only registered model."],
        plain_language_summary=(
            "The confirmed physical parameters instantiate a registered "
            "nonlinear model."
        ),
        equation_latex=[r"\dot{x}=f_{\mathrm{registered}}(x,u)"],
        experiment_proposal={
            "initial_state": model.initial_state,
            "reference": runtime["reference"],
            "horizon_s": runtime["horizon_s"],
            "sample_time_s": runtime["sample_time_s"],
            "actuator_bounds": runtime["actuator_bounds"],
            "state_bounds": runtime["state_bounds"],
            "output_bounds": runtime["output_bounds"],
            "signal_units": model.signal_units,
            "evidence_fact_ids": ["registered_parameters"],
            "registry_policy_id": policy_id,
        },
    )


def confirmed_registered_session(model):
    base = confirmed_pi_tf_session()
    envelope = registered_envelope(model)
    payload = base.model_dump(mode="python")
    payload.update(
        {
            "pending_envelope": envelope,
            "pending_envelope_sha256": _sha256(envelope),
            "confirmed_envelope": envelope,
            "confirmed_envelope_sha256": _sha256(envelope),
        }
    )
    return _rehash(payload)


@pytest.mark.parametrize(
    ("model_factory", "expected_controller_id"),
    [
        (cartpole_model, "cartpole_cascaded"),
        (vtol_model, "vtol_cascaded"),
    ],
)
def test_registered_nonlinear_model_recommends_only_matching_policy(
    model_factory,
    expected_controller_id,
):
    session = confirmed_registered_session(model_factory())

    checked = evaluate_controller_compatibility(
        session,
        expected_revision=session.revision,
    )

    assert checked.state == "controller_replacement_review"
    assert checked.recommended_controller.controller_id == expected_controller_id
    assert checked.compatibility_result.replacement_policy_id.endswith("/v1")


def test_confirmed_vtol_replacement_runs_five_registered_scenarios():
    session = confirmed_registered_session(vtol_model())
    checked = evaluate_controller_compatibility(
        session,
        expected_revision=session.revision,
    )
    ready = confirm_recommended_controller(
        checked,
        replacement_sha256=checked.replacement_sha256,
        expected_revision=checked.revision,
    )
    simulation = create_simulation_from_discovery(
        ready,
        expected_revision=ready.revision,
    )

    completed = run_next_trial(simulation)

    assert len(completed.trials[-1].traces) == 5
