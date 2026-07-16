from __future__ import annotations

from collections import Counter
from pathlib import Path
import math

import numpy as np
from scipy import signal

from cfdc.models import (
    CapabilityGap,
    EvidenceReadinessDecision,
    EvidenceRequirementPlan,
    PlantEvidencePackage,
    RegisteredNonlinearModelSpec,
    StateSpaceModelSpec,
    SystemDescription,
    TransferFunctionModelSpec,
)
from cfdc.evidence.units import time_unit_scale_seconds


def _gap(code: str, capability_id: str, explanation: str, next_action: str) -> CapabilityGap:
    return CapabilityGap(
        code=code,
        stage="object_evidence",
        capability_id=capability_id,
        explanation=explanation,
        resolvable_by_measurement=True,
        required_next_action=next_action,
    )


def _linear_model_modes(model):
    if isinstance(model, TransferFunctionModelSpec):
        denominator = np.trim_zeros(np.asarray(model.denominator, dtype=float), "f")
        numerator = np.trim_zeros(np.asarray(model.numerator, dtype=float), "f")
        poles = np.roots(denominator) if denominator.size > 1 else np.asarray([])
        zeros = np.roots(numerator) if numerator.size > 1 else np.asarray([])
        return denominator.size - 1, poles, zeros
    if isinstance(model, StateSpaceModelSpec):
        a = np.asarray(model.a, dtype=float)
        poles = np.linalg.eigvals(a)
        zeros = np.asarray([])
        if len(model.input_signal_ids) == len(model.output_signal_ids) == 1:
            try:
                zeros, _, _ = signal.ss2zpk(
                    a,
                    np.asarray(model.b, dtype=float),
                    np.asarray(model.c, dtype=float),
                    np.asarray(model.d, dtype=float),
                )
            except (ValueError, np.linalg.LinAlgError):
                zeros = np.asarray([])
        return a.shape[0], poles, zeros
    return None


def _normalized_signal_id(value: str) -> str:
    return " ".join(value.replace("_", " ").replace("-", " ").casefold().split())


def _model_signal_ids(model) -> tuple[list[str], list[str]]:
    if isinstance(model, TransferFunctionModelSpec):
        return [model.input_signal_id], [model.output_signal_id]
    return list(model.input_signal_ids), list(model.output_signal_ids)


def _missing_model_signal_units(model) -> list[str]:
    if isinstance(model, TransferFunctionModelSpec):
        missing: list[str] = []
        if model.input_units.strip().casefold() == "unspecified":
            missing.append(model.input_signal_id)
        if model.output_units.strip().casefold() == "unspecified":
            missing.append(model.output_signal_id)
        return missing
    return [
        signal_id
        for signal_id in [*model.input_signal_ids, *model.output_signal_ids]
        if not model.signal_units.get(signal_id, "").strip()
        or model.signal_units[signal_id].strip().casefold() == "unspecified"
    ]


def _model_profile_conflicts(package: PlantEvidencePackage, profile_id: str) -> list[str]:
    if package.model is None or isinstance(package.model, RegisteredNonlinearModelSpec):
        return []
    modes = _linear_model_modes(package.model)
    if modes is None:
        return []
    order, poles, zeros = modes
    is_discrete = package.model.time_domain == "discrete"
    stable = bool(
        poles.size
        and (
            np.all(np.abs(poles) < 1.0 - 1e-8)
            if is_discrete
            else np.all(np.real(poles) < -1e-8)
        )
    )
    conflicts: list[str] = []
    if profile_id in {"first_order_lag", "first_order_lag_with_delay"}:
        if order != 1 or not stable:
            conflicts.append(
                "The supplied model is not a stable first-order object selected by the structural diagnosis."
            )
        if isinstance(package.model, TransferFunctionModelSpec):
            has_delay = package.model.input_delay_s > 1e-9
            if profile_id == "first_order_lag" and has_delay:
                conflicts.append(
                    "The supplied model contains input delay but the selected method profile does not."
                )
            if profile_id == "first_order_lag_with_delay" and not has_delay:
                conflicts.append(
                    "The selected delay profile is not supported by the supplied zero-delay model."
                )
        elif profile_id == "first_order_lag_with_delay":
            conflicts.append(
                "The selected delay profile requires a model representation with an explicit numeric delay."
            )
    elif profile_id == "second_order_oscillator":
        if (
            order != 2
            or not stable
            or poles.size != 2
            or not np.any(np.abs(np.imag(poles)) > 1e-8)
        ):
            conflicts.append(
                "The supplied model does not contain the stable oscillatory second-order mode selected by the diagnosis."
            )
    elif profile_id == "double_integrator":
        integrator_pole = 1.0 if is_discrete else 0.0
        if order not in {1, 2} or poles.size != order or not np.all(
            np.abs(poles - integrator_pole) <= 1e-8
        ):
            conflicts.append(
                "The supplied model does not contain the pure or double integrator mode selected by the diagnosis."
            )
    elif profile_id == "nmp_inverse_response":
        has_nonminimum_phase_zero = bool(
            zeros.size
            and (
                np.any(np.abs(zeros) > 1.0 + 1e-8)
                if is_discrete
                else np.any(np.real(zeros) > 1e-8)
            )
        )
        if not stable or not has_nonminimum_phase_zero:
            conflicts.append(
                "The supplied model does not confirm stable nonminimum-phase inverse-response dynamics."
            )
    elif profile_id == "mimo_2x2_coupled" and (
        not isinstance(package.model, StateSpaceModelSpec) or not stable
    ):
        conflicts.append(
            "The local MIMO method requires a stable state-space model at the declared operating point."
        )
    return conflicts


def validate_evidence_package(
    package: PlantEvidencePackage,
    requirement_plan: EvidenceRequirementPlan,
    description: SystemDescription,
) -> EvidenceReadinessDecision:
    """Fail closed unless supplied evidence can produce every required feature."""

    gaps: list[CapabilityGap] = []
    source_types = []
    if package.plant_id != requirement_plan.plant_id:
        gaps.append(
            _gap(
                "plant_identity_mismatch",
                package.plant_id,
                "The evidence package belongs to a different plant identifier.",
                "recreate the evidence package for the current diagnostic session",
            )
        )
    validation_limits: dict[str, float] = {}
    if package.validation_spec is not None:
        validation_limits = {
            **package.validation_spec.actuator_limits,
            **package.validation_spec.state_limits,
        }
    for name, value in validation_limits.items():
        if name in description.safety_bounds and not math.isclose(
            description.safety_bounds[name],
            value,
            rel_tol=1e-9,
            abs_tol=1e-12,
        ):
            gaps.append(
                _gap(
                    "safety_boundary_conflict",
                    name,
                    f"Safety boundary '{name}' differs between the object description and validation scenario.",
                    "review the object boundary and submit one consistent value",
                )
            )
    combined_safety = {**description.safety_bounds, **validation_limits}
    if not combined_safety:
        gaps.append(
            _gap(
                "missing_safety_bounds",
                "safety_bounds",
                "Object-specific actuator and state bounds are required before evidence experiments or controller synthesis.",
                "declare reviewed actuator and state safety bounds",
            )
        )

    if package.model is not None:
        source_types.append("mathematical_model")
        model_inputs, model_outputs = _model_signal_ids(package.model)
        missing_units = _missing_model_signal_units(package.model)
        if missing_units:
            gaps.append(
                _gap(
                    "missing_model_signal_units",
                    package.model.kind,
                    "The model is missing explicit units for signal(s): "
                    + ", ".join(missing_units)
                    + ".",
                    "declare a unit string for every model input and output; arbitrary domain-specific units are accepted",
                )
            )
        described_inputs = {
            _normalized_signal_id(value) for value in description.actuators
        }
        described_outputs = {
            _normalized_signal_id(value) for value in description.observed_outputs
        }
        unmatched_inputs = [
            value
            for value in model_inputs
            if described_inputs
            and _normalized_signal_id(value) not in described_inputs
        ]
        unmatched_outputs = [
            value
            for value in model_outputs
            if described_outputs
            and _normalized_signal_id(value) not in described_outputs
        ]
        if unmatched_inputs or unmatched_outputs:
            gaps.append(
                _gap(
                    "model_signal_identity_mismatch",
                    package.model.kind,
                    "Model signal identifiers are not bound to the diagnosed object; "
                    f"unmatched inputs={unmatched_inputs}, outputs={unmatched_outputs}.",
                    "map every model input and output to a named actuator or observed output from this diagnosis",
                )
            )
        for conflict in _model_profile_conflicts(
            package,
            requirement_plan.method_profile_id,
        ):
            gaps.append(
                _gap(
                    "model_profile_conflict",
                    requirement_plan.method_profile_id,
                    conflict,
                    "repeat structural diagnosis or provide a model matching the selected method profile",
                )
            )
        if description.time_scale_hint_s is None:
            gaps.append(
                _gap(
                    "missing_model_experiment_time_scale",
                    "time_scale_hint_s",
                    "A model experiment needs an object-specific time scale; a one-second fallback is not allowed.",
                    "declare the dominant time scale or provide measured timestamps",
                )
            )
        if isinstance(package.model, StateSpaceModelSpec):
            output_count = len(package.model.output_signal_ids)
            input_count = len(package.model.input_signal_ids)
            expected_channels = (
                (2, 2)
                if requirement_plan.method_profile_id == "mimo_2x2_coupled"
                else (1, 1)
            )
            if (input_count, output_count) != expected_channels:
                expected_inputs, expected_outputs = expected_channels
                gaps.append(
                    _gap(
                        "model_profile_channel_mismatch",
                        requirement_plan.method_profile_id,
                        "The selected method profile requires exactly "
                        f"{expected_inputs} model input(s) and {expected_outputs} output(s); "
                        f"the supplied model declares {input_count} and {output_count}.",
                        "repeat structural diagnosis or submit a model with exactly the channels controlled by this profile",
                    )
                )
            if "local_gain_matrix" in requirement_plan.required_feature_ids and (
                input_count < 2 or output_count < 2
            ):
                gaps.append(
                    _gap(
                        "insufficient_model_channels",
                        "local_gain_matrix",
                        "The selected MIMO method requires at least two model inputs and two outputs.",
                        "provide a state-space model covering every scanned input and output",
                    )
                )
        elif "local_gain_matrix" in requirement_plan.required_feature_ids:
            gaps.append(
                _gap(
                    "unsupported_model_for_mimo_scan",
                    "local_gain_matrix",
                    "A scalar transfer function or registered nonlinear template cannot supply a generic MIMO gain matrix.",
                    "provide a compatible MIMO state-space model or measured bounded-scan traces",
                )
            )
        if isinstance(package.model, RegisteredNonlinearModelSpec):
            if package.model.template_id != requirement_plan.method_profile_id:
                gaps.append(
                    _gap(
                        "nonlinear_template_profile_mismatch",
                        package.model.template_id,
                        "The registered nonlinear model does not match the selected control-method profile.",
                        "select the matching template or repeat structural diagnosis",
                    )
                )

    if package.measured_traces:
        source_types.append("measured_traces")
        repeats: Counter[str] = Counter()
        seen_repeat_indices: set[tuple[str, int]] = set()
        seen_trial_ids: set[str] = set()
        for manifest in package.measured_traces:
            primitive = str(manifest.primitive)
            repeat_key = (primitive, manifest.repeat_index)
            duplicate_parts: list[str] = []
            if repeat_key in seen_repeat_indices:
                duplicate_parts.append(
                    f"repeat_index {manifest.repeat_index} for '{primitive}'"
                )
            if manifest.trial_id in seen_trial_ids:
                duplicate_parts.append(f"trial_id '{manifest.trial_id}'")
            if duplicate_parts:
                gaps.append(
                    _gap(
                        "duplicate_measured_repeat",
                        manifest.trial_id,
                        "Measured repeats must be independent; duplicate "
                        + " and ".join(duplicate_parts)
                        + " was supplied.",
                        "provide a separately recorded trial with a unique trial ID and repeat index",
                    )
                )
            else:
                repeats[primitive] += 1
            seen_repeat_indices.add(repeat_key)
            seen_trial_ids.add(manifest.trial_id)
        covered_features = {
            feature_id
            for manifest in package.measured_traces
            for feature_id in manifest.estimates
        }
        missing_features = set(requirement_plan.required_feature_ids) - covered_features
        for feature_id in sorted(missing_features):
            gaps.append(
                _gap(
                    "missing_measured_feature_evidence",
                    feature_id,
                    f"No measured trace is declared to estimate required feature '{feature_id}'.",
                    "upload a trace using the required experiment primitive and signal mapping",
                )
            )
        for requirement in requirement_plan.experiment_requirements:
            if not set(requirement.feature_ids).intersection(covered_features):
                continue
            if repeats[requirement.primitive] < requirement.minimum_measured_repeats:
                gaps.append(
                    _gap(
                        "insufficient_measured_repeats",
                        requirement.primitive,
                        f"Measured experiment '{requirement.primitive}' requires at least {requirement.minimum_measured_repeats} valid repeats.",
                        "upload additional independent repeats in the same operating region",
                    )
                )
        for manifest in package.measured_traces:
            path = Path(manifest.csv_path)
            if path.suffix.lower() != ".csv" or not path.is_file():
                gaps.append(
                    _gap(
                        "missing_or_invalid_csv",
                        manifest.trial_id,
                        f"Measured trace file '{manifest.csv_path}' is not an existing CSV file.",
                        "provide an existing CSV file for this trial",
                    )
                )
            required_units = {"time", *manifest.signal_columns}
            if not required_units.issubset(manifest.signal_units):
                gaps.append(
                    _gap(
                        "missing_signal_units",
                        manifest.trial_id,
                        "Every mapped signal and the time column require explicit units.",
                        "declare units for time and every canonical signal mapping",
                    )
                )
            elif "time" in manifest.signal_units:
                try:
                    time_unit_scale_seconds(manifest.signal_units["time"])
                except ValueError as exc:
                    gaps.append(
                        _gap(
                            "invalid_time_unit",
                            manifest.trial_id,
                            str(exc),
                            "declare the timestamp unit using a duration unit such as s or ms",
                        )
                    )

    return EvidenceReadinessDecision(
        decision="rejected" if gaps else "ready",
        source_types=source_types,
        gaps=gaps,
    )
