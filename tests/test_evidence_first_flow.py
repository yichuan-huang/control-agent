import numpy as np
import pytest
from pydantic import ValidationError

from cfdc.diagnosis import start_diagnostic_session, submit_evidence_to_session
from cfdc.evidence import (
    build_evidence_requirement_plan,
    load_measured_experiments,
    validate_evidence_package,
)
from cfdc.features import extract_features_from_result
from cfdc.models import (
    ClosedLoopValidationSpec,
    ExperimentTrace,
    MeasuredTraceManifest,
    PlantEvidencePackage,
    RegisteredNonlinearModelSpec,
    SimulationExperimentRecord,
    StateSpaceModelSpec,
    SystemDescription,
    TransferFunctionModelSpec,
)
from cfdc.runtime import run_cfdc_route
from cfdc.workflow import (
    default_control_method_profile_catalog,
    default_demo_plant_fixture_catalog,
)


def _first_order_description() -> SystemDescription:
    return SystemDescription(
        text="A measured first order heater settles after a small power change.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )


def _parameterized_first_order_description() -> SystemDescription:
    return SystemDescription(
        text="A measured first order heater settles after a small power change.",
        observed_outputs=["temperature"],
        actuators=["heater"],
        safety_bounds={
            "input_min": -1.0,
            "input_max": 1.0,
            "output_min": -10.0,
            "output_max": 10.0,
        },
        time_scale_hint_s=4.0,
    )


def _transfer_function_evidence(description, *, gain: float, tau: float):
    preliminary = run_cfdc_route("generic", description=description)
    return PlantEvidencePackage(
        plant_id=preliminary.evidence_requirement_plan.plant_id,
        model=TransferFunctionModelSpec(
            numerator=[gain],
            denominator=[tau, 1.0],
            input_signal_id="heater",
            output_signal_id="temperature",
            input_units="normalized_power",
            output_units="normalized_temperature",
        ),
        provenance=["user supplied transfer function"],
    )


def _validation_spec() -> ClosedLoopValidationSpec:
    return ClosedLoopValidationSpec(
        reference={"temperature": 1.0},
        horizon_s=1000.0,
        sample_time_s=0.1,
        actuator_limits={"input_min": -1.0, "input_max": 1.0},
        state_limits={"output_min": -10.0, "output_max": 10.0},
        performance_limits={
            "max_abs_final_error": 0.05,
            "max_overshoot": 0.25,
            "max_settling_time_s": 950.0,
            "max_saturation_fraction": 0.2,
        },
    )


def test_complete_structural_diagnosis_waits_for_object_evidence():
    report = run_cfdc_route("generic", description=_first_order_description())

    assert report.status == "awaiting_specifications"
    assert report.diagnosis is not None and report.diagnosis.complete
    assert report.classification is not None
    assert report.evidence_requirement_plan is not None
    assert report.experiment_results == []
    assert report.features == []
    assert report.controller is None
    assert report.algorithm1_state is None
    assert report.evidence_boundary == "structural_diagnosis_only"


def test_missing_object_specs_never_call_demo_profile_experiments():
    def forbidden_profile_runner(*args, **kwargs):
        raise AssertionError("demo profile experiments must not run for a user object")

    report = run_cfdc_route(
        "generic",
        description=_first_order_description(),
        experiment_runner=forbidden_profile_runner,
    )

    assert report.status == "awaiting_specifications"


def test_evidence_requirement_plan_is_specific_to_required_features():
    report = run_cfdc_route("generic", description=_first_order_description())
    plan = build_evidence_requirement_plan(
        report.system_description,
        report.diagnosis,
        report.classification,
        report.semantic_selection,
    )

    assert plan.required_feature_ids == ["static_gain", "time_constant"]
    assert plan.accepted_sources == [
        "declared_specification",
        "structured_mathematical_model",
        "measured_traces_reserved_for_later",
    ]
    assert plan.experiment_requirements[0].required_signal_ids == [
        "time",
        "input",
        "output",
    ]
    assert "safety_bounds" in plan.missing_items
    assert "time_scale_hint_s" in plan.missing_items


def test_transfer_function_model_rejects_missing_discrete_sample_time():
    with pytest.raises(ValidationError, match="sample_time_s"):
        TransferFunctionModelSpec(
            numerator=[1.0],
            denominator=[1.0, 1.0],
            time_domain="discrete",
            input_signal_id="heater",
            output_signal_id="temperature",
        )


def test_stable_discrete_first_order_model_is_accepted_and_executed():
    description = _parameterized_first_order_description()
    preliminary = run_cfdc_route("generic", description=description)
    package = PlantEvidencePackage(
        plant_id=preliminary.evidence_requirement_plan.plant_id,
        model=TransferFunctionModelSpec(
            numerator=[0.1],
            denominator=[1.0, -0.9],
            time_domain="discrete",
            sample_time_s=0.1,
            input_signal_id="heater",
            output_signal_id="temperature",
            input_units="V",
            output_units="degC",
        ),
    )

    report = run_cfdc_route(
        "generic",
        description=description,
        evidence_package=package,
    )

    assert report.status == "validation_pending"
    assert report.features


def test_unstable_discrete_first_order_model_conflicts_with_stable_profile():
    description = _parameterized_first_order_description()
    preliminary = run_cfdc_route("generic", description=description)
    package = PlantEvidencePackage(
        plant_id=preliminary.evidence_requirement_plan.plant_id,
        model=TransferFunctionModelSpec(
            numerator=[0.1],
            denominator=[1.0, -1.1],
            time_domain="discrete",
            sample_time_s=0.1,
            input_signal_id="heater",
            output_signal_id="temperature",
        ),
    )

    decision = validate_evidence_package(
        package,
        preliminary.evidence_requirement_plan,
        description,
    )

    assert decision.decision == "rejected"
    assert any(gap.code == "model_profile_conflict" for gap in decision.gaps)


def test_model_signal_names_must_belong_to_the_diagnosed_object():
    description = _parameterized_first_order_description()
    preliminary = run_cfdc_route("generic", description=description)
    package = PlantEvidencePackage(
        plant_id=preliminary.evidence_requirement_plan.plant_id,
        model=TransferFunctionModelSpec(
            numerator=[1.0],
            denominator=[2.0, 1.0],
            input_signal_id="unrelated_valve",
            output_signal_id="unrelated_pressure",
        ),
    )

    decision = validate_evidence_package(
        package,
        preliminary.evidence_requirement_plan,
        description,
    )

    assert decision.decision == "rejected"
    assert any(gap.code == "model_signal_identity_mismatch" for gap in decision.gaps)


def test_model_with_missing_signal_units_returns_a_specific_evidence_gap():
    description = _parameterized_first_order_description()
    preliminary = run_cfdc_route("generic", description=description)
    package = PlantEvidencePackage(
        plant_id=preliminary.evidence_requirement_plan.plant_id,
        model=TransferFunctionModelSpec(
            numerator=[1.0],
            denominator=[2.0, 1.0],
            input_signal_id="heater",
            output_signal_id="temperature",
        ),
    )

    decision = validate_evidence_package(
        package,
        preliminary.evidence_requirement_plan,
        description,
    )

    assert decision.decision == "rejected"
    assert any(gap.code == "missing_model_signal_units" for gap in decision.gaps)


def test_registered_nonlinear_model_rejects_partial_fixture_parameters():
    with pytest.raises(ValidationError, match="complete parameter set"):
        RegisteredNonlinearModelSpec(
            template_id="underactuated_cartpole",
            parameters={"cart_mass_kg": 2.0},
            initial_state={
                "position_m": 0.0,
                "velocity_m_s": 0.0,
                "angle_rad": 0.0,
                "angular_rate_rad_s": 0.0,
            },
            input_signal_ids=["force"],
            output_signal_ids=["position", "angle"],
        )


def test_registered_nonlinear_model_rejects_nonphysical_parameters():
    with pytest.raises(ValidationError, match="cart_mass_kg"):
        RegisteredNonlinearModelSpec(
            template_id="underactuated_cartpole",
            parameters={
                "cart_mass_kg": -0.5,
                "pole_mass_kg": 0.2,
                "com_length_m": 0.3,
                "pole_inertia_kg_m2": 0.006,
                "cart_friction_n_s_m": 0.1,
                "gravity_m_s2": 9.81,
                "force_limit_n": 10.0,
                "cart_position_limit_m": 2.4,
            },
            initial_state={
                "position_m": 0.0,
                "velocity_m_s": 0.0,
                "angle_rad": 0.0,
                "angular_rate_rad_s": 0.0,
            },
            input_signal_ids=["force"],
            output_signal_ids=["position", "angle"],
            signal_units={"force": "N", "position": "m", "angle": "rad"},
        )


def test_state_space_model_requires_an_explicit_initial_state():
    with pytest.raises(ValidationError, match="initial_state"):
        StateSpaceModelSpec(
            a=[[-1.0]],
            b=[[1.0]],
            c=[[1.0]],
            d=[[0.0]],
            state_names=["temperature_state"],
            input_signal_ids=["heater"],
            output_signal_ids=["temperature"],
        )


def test_scalar_profile_rejects_state_space_model_with_hidden_extra_channels():
    description = _parameterized_first_order_description()
    preliminary = run_cfdc_route("generic", description=description)
    package = PlantEvidencePackage(
        plant_id=preliminary.evidence_requirement_plan.plant_id,
        model=StateSpaceModelSpec(
            a=[[-1.0]],
            b=[[1.0, 0.5]],
            c=[[1.0], [0.2]],
            d=[[0.0, 0.0], [0.0, 0.0]],
            state_names=["temperature_state"],
            input_signal_ids=["heater", "bypass"],
            output_signal_ids=["temperature", "secondary_temperature"],
            initial_state=[0.0],
        ),
    )

    decision = validate_evidence_package(
        package,
        preliminary.evidence_requirement_plan,
        description,
    )

    assert decision.decision == "rejected"
    assert any(gap.code == "model_profile_channel_mismatch" for gap in decision.gaps)


def test_evidence_package_requires_model_or_measured_traces():
    with pytest.raises(ValidationError, match="model or measured trace"):
        PlantEvidencePackage(plant_id="heater-1")


def test_two_same_class_models_produce_object_specific_features_and_gains():
    description = _parameterized_first_order_description()
    first = run_cfdc_route(
        "generic",
        description=description,
        evidence_package=_transfer_function_evidence(description, gain=1.0, tau=2.0),
    )
    second = run_cfdc_route(
        "generic",
        description=description,
        evidence_package=_transfer_function_evidence(description, gain=3.0, tau=8.0),
    )

    assert first.status == second.status == "validation_pending"
    assert (
        first.controller.release_level
        == second.controller.release_level
        == "candidate_unvalidated"
    )
    first_features = {item.feature_id: item.value for item in first.features}
    second_features = {item.feature_id: item.value for item in second.features}
    assert first_features["static_gain"] != pytest.approx(
        second_features["static_gain"]
    )
    assert first_features["time_constant"] != pytest.approx(
        second_features["time_constant"]
    )
    assert first.final_gains != second.final_gains
    assert all(
        item.plant_id == first.evidence_requirement_plan.plant_id
        for item in first.features
    )
    assert first.algorithm1_state is None


def test_measured_traces_release_only_an_unvalidated_candidate(tmp_path):
    description = _parameterized_first_order_description()
    preliminary = run_cfdc_route("generic", description=description)
    manifests = []
    time_s = np.linspace(0.0, 30.0, 601)
    input_signal = np.where(time_s >= 2.0, 0.2, 0.0)
    for repeat_index in range(1, 4):
        output = np.where(
            time_s >= 2.0,
            0.4 * (1.0 - np.exp(-(time_s - 2.0) / 5.0)),
            0.0,
        )
        path = tmp_path / f"step-{repeat_index}.csv"
        np.savetxt(
            path,
            np.column_stack((time_s, input_signal, output)),
            delimiter=",",
            header="time,heater,temperature",
            comments="",
        )
        manifests.append(
            MeasuredTraceManifest(
                csv_path=str(path),
                primitive="ramp_step",
                repeat_index=repeat_index,
                time_column="time",
                signal_columns={"input": "heater", "output": "temperature"},
                signal_units={
                    "time": "s",
                    "input": "normalized_power",
                    "output": "normalized_temperature",
                },
                estimates=["static_gain", "time_constant"],
                operating_region="nominal heating region",
                trial_id=f"trial-{repeat_index}",
                data_source="bench recording",
            )
        )
    package = PlantEvidencePackage(
        plant_id=preliminary.evidence_requirement_plan.plant_id,
        measured_traces=manifests,
    )

    report = run_cfdc_route(
        "generic",
        description=description,
        evidence_package=package,
    )

    assert report.status == "candidate_unvalidated"
    assert report.controller.release_level == "candidate_unvalidated"
    assert report.features
    assert all(item.evidence_source == "measured_trace" for item in report.features)
    assert report.algorithm1_state is None
    assert report.stale_controller_performance is None
    assert report.adapted_controller_performance is None


def test_measured_trace_time_values_are_converted_to_seconds(tmp_path):
    path = tmp_path / "millisecond-trace.csv"
    np.savetxt(
        path,
        np.asarray([[0.0, 0.0], [10.0, 1.0], [20.0, 2.0]]),
        delimiter=",",
        header="time,output",
        comments="",
    )
    manifest = MeasuredTraceManifest(
        csv_path=str(path),
        primitive="ramp_step",
        repeat_index=1,
        time_column="time",
        signal_columns={"output": "output"},
        signal_units={"time": "ms", "output": "degC"},
        estimates=["time_constant"],
        operating_region="nominal",
        trial_id="trial-ms",
        data_source="uploaded recording",
    )
    package = PlantEvidencePackage(
        plant_id="plant-time-unit",
        measured_traces=[manifest],
    )

    record = load_measured_experiments(package)[0]

    assert record.trace.time_s == pytest.approx([0.0, 0.01, 0.02])
    assert record.trace.metadata["signal_units"]["time"] == "s"


def test_measured_trace_rejects_a_non_time_unit_for_timestamp_column(tmp_path):
    path = tmp_path / "bad-time-unit.csv"
    path.write_text("time,output\n0,0\n1,1\n", encoding="utf-8")
    manifest = MeasuredTraceManifest(
        csv_path=str(path),
        primitive="ramp_step",
        repeat_index=1,
        time_column="time",
        signal_columns={"output": "output"},
        signal_units={"time": "kg", "output": "degC"},
        estimates=["time_constant"],
        operating_region="nominal",
        trial_id="trial-bad-time",
        data_source="uploaded recording",
    )
    package = PlantEvidencePackage(
        plant_id="plant-time-unit",
        measured_traces=[manifest],
    )

    with pytest.raises(ValueError, match="time unit"):
        load_measured_experiments(package)


def test_duplicate_measured_trial_does_not_count_as_three_independent_repeats(tmp_path):
    description = _parameterized_first_order_description()
    preliminary = run_cfdc_route("generic", description=description)
    path = tmp_path / "one-trial.csv"
    path.write_text(
        "time,input,output\n0,0,0\n1,1,0.5\n2,1,1\n",
        encoding="utf-8",
    )
    manifest = MeasuredTraceManifest(
        csv_path=str(path),
        primitive="ramp_step",
        repeat_index=1,
        time_column="time",
        signal_columns={"input": "input", "output": "output"},
        signal_units={"time": "s", "input": "V", "output": "degC"},
        estimates=["static_gain", "time_constant"],
        operating_region="nominal",
        trial_id="same-trial",
        data_source="uploaded recording",
    )
    package = PlantEvidencePackage(
        plant_id=preliminary.evidence_requirement_plan.plant_id,
        measured_traces=[manifest, manifest, manifest],
    )

    decision = validate_evidence_package(
        package,
        preliminary.evidence_requirement_plan,
        description,
    )

    assert decision.decision == "rejected"
    assert any(gap.code == "duplicate_measured_repeat" for gap in decision.gaps)


def test_model_with_explicit_validation_requirements_can_be_simulation_validated():
    description = _parameterized_first_order_description()
    package = _transfer_function_evidence(description, gain=1.0, tau=2.0)
    package = package.model_copy(update={"validation_spec": _validation_spec()})

    report = run_cfdc_route(
        "generic",
        description=description,
        evidence_package=package,
    )

    assert report.status == "validated_in_simulation"
    assert report.controller.release_level == "validated_in_simulation"
    assert report.controller_validation.status == "passed"
    assert report.controller_validation.performance.success
    assert report.evidence_boundary == "user_object_model_validated_in_simulation"


def test_validation_spec_can_supply_controller_actuator_and_state_bounds():
    description = _parameterized_first_order_description().model_copy(
        update={"safety_bounds": {}}
    )
    package = _transfer_function_evidence(description, gain=1.0, tau=2.0)
    package = package.model_copy(update={"validation_spec": _validation_spec()})

    report = run_cfdc_route(
        "generic",
        description=description,
        evidence_package=package,
    )

    assert report.status == "validated_in_simulation"
    assert report.controller.saturation == {
        "input_min": -1.0,
        "input_max": 1.0,
    }


def test_siso_validation_does_not_ignore_extra_reference_channels():
    description = _parameterized_first_order_description()
    package = _transfer_function_evidence(description, gain=1.0, tau=2.0)
    validation = _validation_spec().model_copy(
        update={"reference": {"temperature": 1.0, "pressure": 2.0}}
    )
    package = package.model_copy(update={"validation_spec": validation})

    report = run_cfdc_route(
        "generic",
        description=description,
        evidence_package=package,
    )

    assert report.status == "rejected"
    assert report.controller_validation.status == "not_supported"
    assert any(
        "exactly one reference" in item
        for item in report.controller_validation.violations
    )


def test_siso_validation_does_not_ignore_unexecutable_initial_state():
    description = _parameterized_first_order_description()
    package = _transfer_function_evidence(description, gain=1.0, tau=2.0)
    validation = _validation_spec().model_copy(
        update={"initial_state": {"temperature": 0.5}}
    )
    package = package.model_copy(update={"validation_spec": validation})

    report = run_cfdc_route(
        "generic",
        description=description,
        evidence_package=package,
    )

    assert report.status == "rejected"
    assert report.controller_validation.status == "not_supported"
    assert any(
        "initial_state" in item for item in report.controller_validation.violations
    )


@pytest.mark.parametrize(
    ("field", "missing_key"),
    [
        ("actuator_limits", "input_min"),
        ("state_limits", "output_max"),
        ("performance_limits", "max_settling_time_s"),
    ],
)
def test_validation_spec_rejects_missing_required_limit_keys(field, missing_key):
    payload = _validation_spec().model_dump()
    payload[field].pop(missing_key)

    with pytest.raises(ValidationError, match=missing_key):
        ClosedLoopValidationSpec.model_validate(payload)


def test_standard_profile_requires_explicit_demo_mode_and_stays_demo_only():
    description = _parameterized_first_order_description()
    report = run_cfdc_route(
        "generic",
        description=description,
        execution_mode="demo_fixture",
    )

    assert report.status == "demo_completed"
    assert report.controller.release_level == "demo_fixture_only"
    assert report.evidence_boundary == "demo_fixture_only"


def test_method_profiles_do_not_contain_demo_simulator_parameters():
    methods = default_control_method_profile_catalog()
    fixtures = default_demo_plant_fixture_catalog()

    first_order = next(
        item for item in methods.profiles if item.profile_id == "first_order_lag"
    )
    first_order_fixture = next(
        item
        for item in fixtures.fixtures
        if item.method_profile_id == "first_order_lag"
    )
    assert not hasattr(first_order, "simulator_backend")
    assert not hasattr(first_order, "nominal_parameters")
    assert first_order.required_feature_ids == ["static_gain", "time_constant"]
    assert first_order_fixture.simulator_backend == "scalar_first_order"
    assert first_order_fixture.nominal_parameters == {
        "static_gain": 2.0,
        "time_constant": 5.0,
    }


def test_mimo_local_time_constant_is_estimated_from_transition_data():
    time_s = np.linspace(0.0, 30.0, 3001)
    u1 = np.where((time_s >= 2.0) & (time_s < 12.0), 0.4, 0.0)
    u2 = np.where((time_s >= 17.0) & (time_s < 27.0), 0.4, 0.0)
    target = np.column_stack((2.0 * u1 + 0.7 * u2, 0.5 * u1 + 1.6 * u2))
    outputs = np.zeros_like(target)
    dt = time_s[1] - time_s[0]
    tau = 2.0
    for index in range(1, len(time_s)):
        outputs[index] = (
            outputs[index - 1] + dt * (target[index - 1] - outputs[index - 1]) / tau
        )
    record = SimulationExperimentRecord(
        primitive="bounded_scan",
        estimates=["local_gain_matrix", "local_time_constant", "pairing_indicator"],
        trace=ExperimentTrace(
            time_s=time_s.tolist(),
            signals={
                "input_1": u1.tolist(),
                "input_2": u2.tolist(),
                "output_1": outputs[:, 0].tolist(),
                "output_2": outputs[:, 1].tolist(),
            },
        ),
    )

    features = {item.feature_id: item for item in extract_features_from_result(record)}

    assert features["local_time_constant"].value == pytest.approx(2.0, rel=0.08)
    assert features["local_time_constant"].method == "mimo_step_63_percent_transition"
    assert np.asarray(features["local_gain_matrix"].value) == pytest.approx(
        np.asarray([[2.0, 0.7], [0.5, 1.6]]), rel=0.03
    )


def test_user_object_controller_does_not_invent_unbounded_saturation_limits():
    description = _parameterized_first_order_description().model_copy(
        update={"safety_bounds": {"input_range": 2.0}}
    )
    report = run_cfdc_route(
        "generic",
        description=description,
        evidence_package=_transfer_function_evidence(description, gain=1.0, tau=2.0),
    )

    assert report.status == "rejected"
    assert report.controller.release_level == "refuse"
    assert report.final_gains == {}
    assert any("input_min" in note and "input_max" in note for note in report.notes)


def test_model_that_conflicts_with_selected_method_profile_is_rejected_before_experiments():
    description = _parameterized_first_order_description()
    preliminary = run_cfdc_route("generic", description=description)
    package = PlantEvidencePackage(
        plant_id=preliminary.evidence_requirement_plan.plant_id,
        model=TransferFunctionModelSpec(
            numerator=[1.0],
            denominator=[1.0, -1.0],
            input_signal_id="heater",
            output_signal_id="temperature",
        ),
    )

    readiness = validate_evidence_package(
        package,
        preliminary.evidence_requirement_plan,
        description,
    )

    assert readiness.decision == "rejected"
    assert any(gap.code == "model_profile_conflict" for gap in readiness.gaps)


def test_repeated_features_from_different_operating_regions_are_not_averaged():
    time_s = np.linspace(0.0, 20.0, 401)
    input_signal = np.where(time_s >= 2.0, 1.0, 0.0)
    output = np.where(
        time_s >= 2.0,
        2.0 * (1.0 - np.exp(-(time_s - 2.0) / 3.0)),
        0.0,
    )
    records = [
        SimulationExperimentRecord(
            primitive="ramp_step",
            estimates=["static_gain", "time_constant"],
            repeat_index=index,
            operating_region=region,
            trace=ExperimentTrace(
                time_s=time_s.tolist(),
                signals={"input": input_signal.tolist(), "output": output.tolist()},
            ),
        )
        for index, region in enumerate(("low load", "high load"), start=1)
    ]

    from cfdc.features import extract_features_from_repeated_results

    with pytest.raises(ValueError, match="operating region"):
        extract_features_from_repeated_results(records)


def test_diagnostic_session_requires_evidence_after_eight_fields():
    description = _parameterized_first_order_description()
    state = start_diagnostic_session(description)

    assert state.schema_version == "3.0"
    assert state.status == "awaiting_specifications"
    assert state.evidence_requirement_plan is not None

    package = _transfer_function_evidence(description, gain=1.0, tau=2.0)
    updated = submit_evidence_to_session(state, package)

    assert updated.status == "ready_for_experiments"
    assert updated.evidence_readiness.decision == "ready"


def test_ready_for_experiments_requires_a_positive_evidence_decision():
    description = _parameterized_first_order_description()
    state = start_diagnostic_session(description).model_copy(
        update={"status": "ready_for_experiments", "evidence_readiness": None}
    )

    with pytest.raises(ValueError, match="missing validated object evidence"):
        run_cfdc_route(diagnostic_session_state=state)
