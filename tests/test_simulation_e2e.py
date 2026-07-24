from __future__ import annotations

from cfdc.diagnosis import DiagnosticEngine
from cfdc.lab import (
    ModelProposalContext,
    SimulationRunConfig,
    approve_llm_proposal,
    bootstrap_controller_candidate,
    confirm_model,
    create_free_input_session,
    export_session,
    request_gain_for_session,
    request_model_for_session,
    run_deterministic_auto,
    run_next_trial,
    set_initial_controller,
)
from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    ControllerCandidate,
    StructuralDiagnosis,
    SystemDescription,
)
from tests.simulation_fixtures import cartpole_session, continuous_siso_session


def test_e2e_continuous_siso_stops_on_first_stability():
    session = continuous_siso_session()
    session = run_deterministic_auto(session)
    assert session.state == "stable"
    assert len(session.trials) == 1
    trial = session.trials[0]
    assert trial.stability.analysis_domain == "continuous"
    assert all(pole.real < -1e-6 for pole in trial.stability.poles)
    assert trial.stability.trajectory_finite
    assert trial.stability.trajectory_bounded
    assert len(trial.trial_hash) == 64
    assert "performance optimization was run" in session.termination_reason


def test_e2e_registered_cartpole_reaches_stability_after_multiple_rounds():
    session = cartpole_session()
    session = run_deterministic_auto(session)
    assert session.state == "stable"
    assert 2 <= len(session.trials) <= 20
    assert all(len(trial.traces) == 5 for trial in session.trials)
    assert all(len(trial.stability.poles) == 4 for trial in session.trials)
    assert all(len(trial.stability.scenario_evidence) == 5 for trial in session.trials)
    assert all(
        evidence.passed for evidence in session.trials[-1].stability.scenario_evidence
    )
    assert session.llm_calls == []


def _unstable_siso_context():
    description = SystemDescription(
        text="A locally linear SISO plant with one actuator and one output.",
        observed_outputs=["y"],
        actuators=["u"],
    )
    base_description = SystemDescription(
        text=(
            "A stable first-order process with one actuator and one output "
            "has no delay and is locally linear."
        ),
        observed_outputs=["y"],
        actuators=["u"],
    )
    diagnosis, _ = DiagnosticEngine().run(base_description)
    payload = diagnosis.model_dump(mode="python")
    payload["open_loop_stability"].update(
        {
            "status": "known",
            "value": "open-loop response diverges",
            "assessment": "unstable",
            "confidence": 0.95,
            "evidence": ["explicit open-loop divergence"],
        }
    )
    diagnosis = StructuralDiagnosis.model_validate(payload)
    classification = ArchetypeClassification(
        primary_class=(ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP),
        control_architecture="detuned PI",
        required_core_features=["input_gain"],
        rationale="the supplied local pole is unstable",
    )
    return ModelProposalContext(
        description=description,
        diagnosis=diagnosis,
        classification=classification,
    )


class _FreeInputAdapter:
    base_url = "https://example.test/v1"
    model = "audited-fake"
    api_key = "NEVER-EXPORT-THIS-KEY"

    def propose_model(self, _context):
        return {
            "status": "ready",
            "model": {
                "kind": "transfer_function",
                "numerator": [1.0],
                "denominator": [1.0, -1.0],
                "input_signal_id": "u",
                "output_signal_id": "y",
                "input_units": "V",
                "output_units": "m",
            },
            "confidence": 0.92,
            "assumptions": ["local continuous LTI hypothesis"],
            "evidence": ["user supplied the numeric pole and signal units"],
            "questions": [],
        }

    def propose_gain_update(self, _context):
        return {
            "new_parameters": {"kp": 1.008, "ki": 0.1},
            "rationale": (
                "move the whitelisted proportional gain by five percent "
                "across the local stability threshold"
            ),
        }


def test_e2e_free_input_model_confirmation_llm_approval_and_scoped_stability():
    adapter = _FreeInputAdapter()
    session = create_free_input_session()
    session, model_call = request_model_for_session(
        session, adapter, _unstable_siso_context()
    )
    assert model_call.proposal.status == "ready"
    assert session.state == "model_review"
    session = confirm_model(session)

    candidate = ControllerCandidate(
        architecture="detuned_PI",
        gains={"kp": 0.96, "ki": 0.1, "integral_time": 10.0},
        tunable_gain_names=["kp", "ki"],
        status="ready_for_conservative_trial",
    )
    bootstrap = bootstrap_controller_candidate(candidate, session.confirmed_model)
    assert bootstrap.status == "ready"
    session = set_initial_controller(
        session,
        bootstrap.controller,
        tuning_profile=bootstrap.tuning_profile,
        run_config=SimulationRunConfig(
            reference={"y": 1.0},
            horizon_s=10.0,
            sample_time_s=0.01,
            actuator_bounds={"u": (-1000.0, 1000.0)},
            output_bounds={"y": (-1000.0, 1000.0)},
        ),
    )
    session = run_next_trial(session)
    assert session.state == "needs_adjustment"

    session, gain_call = request_gain_for_session(session, adapter)
    assert gain_call.proposal.approval_state == "pending"
    assert session.trial_controller.kp == 0.96
    session = approve_llm_proposal(session)
    session = run_next_trial(session)

    assert session.state == "stable"
    assert session.evidence_boundary == "llm_proposed_model_hypothesis"
    assert len(session.llm_calls) == 2
    exported = export_session(session)
    assert "NEVER-EXPORT-THIS-KEY" not in exported
    assert "does not validate a real object" in exported.casefold()
