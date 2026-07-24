from __future__ import annotations

import csv
import hashlib
import math
from dataclasses import MISSING, fields

import numpy as np
from scipy import signal

from cfdc.evidence.units import time_unit_scale_seconds
from cfdc.models import (
    ExperimentPlan,
    ExperimentPrimitive,
    ExperimentTrace,
    MeasuredTraceManifest,
    PlantEvidencePackage,
    RegisteredNonlinearModelSpec,
    SimulationExperimentRecord,
    StateSpaceModelSpec,
    TransferFunctionModelSpec,
)
from cfdc.sim.cartpole import CartpoleParams
from cfdc.sim.traces import hover_trace, modal_trace, vtol_pulse_trace
from cfdc.sim.vtol import VtolParams


def _read_measured_manifest(
    package: PlantEvidencePackage,
    manifest: MeasuredTraceManifest,
) -> SimulationExperimentRecord:
    if "time" not in manifest.signal_units:
        raise ValueError(f"trial '{manifest.trial_id}' must declare the time unit")
    time_scale = time_unit_scale_seconds(manifest.signal_units["time"])
    with open(manifest.csv_path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        required_columns = {manifest.time_column, *manifest.signal_columns.values()}
        missing = required_columns - fieldnames
        if missing:
            raise ValueError(
                f"trial '{manifest.trial_id}' is missing CSV column(s): {', '.join(sorted(missing))}"
            )
        time_s: list[float] = []
        signals = {canonical: [] for canonical in manifest.signal_columns}
        for row_number, row in enumerate(reader, start=2):
            try:
                time_value = float(row[manifest.time_column])
                signal_values = {
                    canonical: float(row[column])
                    for canonical, column in manifest.signal_columns.items()
                }
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"trial '{manifest.trial_id}' contains non-numeric data at CSV row {row_number}"
                ) from exc
            if not math.isfinite(time_value) or any(
                not math.isfinite(value) for value in signal_values.values()
            ):
                raise ValueError(
                    f"trial '{manifest.trial_id}' contains non-finite data at CSV row {row_number}"
                )
            time_s.append(time_value * time_scale)
            for canonical, value in signal_values.items():
                signals[canonical].append(value)
    return SimulationExperimentRecord(
        plant_id=package.plant_id,
        evidence_package_id=package.evidence_package_id,
        evidence_source="measured_trace",
        primitive=manifest.primitive,
        estimates=manifest.estimates,
        repeat_index=manifest.repeat_index,
        experiment_protocol_version="measured-csv-v1",
        operating_region=manifest.operating_region,
        evidence_boundary="user_object_measured_trace",
        trace=ExperimentTrace(
            time_s=time_s,
            signals=signals,
            metadata={
                "signal_units": {**manifest.signal_units, "time": "s"},
                "trial_id": manifest.trial_id,
                "data_source": manifest.data_source,
            },
        ),
        metadata={
            "trial_id": manifest.trial_id,
            "data_source": manifest.data_source,
        },
    )


def load_measured_experiments(
    package: PlantEvidencePackage,
) -> list[SimulationExperimentRecord]:
    return [_read_measured_manifest(package, item) for item in package.measured_traces]


def _instruction_time(
    instruction,
    model: TransferFunctionModelSpec | StateSpaceModelSpec | None = None,
) -> tuple[np.ndarray, float]:
    if instruction.duration_s is None or instruction.sample_rate_hz is None:
        raise ValueError(
            "model experiments require object-specific duration and sample rate"
        )
    if model is not None and model.time_domain == "discrete":
        assert model.sample_time_s is not None
        sample_count = int(np.floor(instruction.duration_s / model.sample_time_s)) + 1
        if sample_count < 3:
            raise ValueError(
                "the discrete model sample time yields fewer than three samples "
                "within the object-specific experiment duration"
            )
        return (
            np.arange(sample_count, dtype=float) * model.sample_time_s,
            float(instruction.input_amplitude or 0.0),
        )
    sample_count = max(
        101, int(instruction.duration_s * instruction.sample_rate_hz) + 1
    )
    return np.linspace(0.0, instruction.duration_s, sample_count), float(
        instruction.input_amplitude or 0.0
    )


def _simulate_linear(
    model: TransferFunctionModelSpec | StateSpaceModelSpec,
    time_s: np.ndarray,
    inputs: np.ndarray,
) -> np.ndarray:
    if isinstance(model, TransferFunctionModelSpec):
        if inputs.ndim != 1:
            raise ValueError("transfer-function evidence supports one input channel")
        delayed = inputs.copy()
        if model.input_delay_s > 0.0:
            delayed = np.interp(
                time_s - model.input_delay_s,
                time_s,
                inputs,
                left=float(inputs[0]),
                right=float(inputs[-1]),
            )
        if model.time_domain == "continuous":
            _, output, _ = signal.lsim(
                signal.TransferFunction(model.numerator, model.denominator),
                U=delayed,
                T=time_s,
            )
        else:
            system = signal.dlti(
                model.numerator,
                model.denominator,
                dt=model.sample_time_s,
            )
            _, output = signal.dlsim(system, delayed, t=time_s)
        return np.asarray(output, dtype=float).reshape(-1, 1)

    a = np.asarray(model.a, dtype=float)
    b = np.asarray(model.b, dtype=float)
    c = np.asarray(model.c, dtype=float)
    d = np.asarray(model.d, dtype=float)
    x0 = np.asarray(model.initial_state or np.zeros(a.shape[0]), dtype=float)
    if model.time_domain == "continuous":
        _, output, _ = signal.lsim(
            signal.StateSpace(a, b, c, d),
            U=inputs,
            T=time_s,
            X0=x0,
        )
    else:
        _, output, _ = signal.dlsim(
            signal.dlti(a, b, c, d, dt=model.sample_time_s),
            u=inputs,
            t=time_s,
            x0=x0,
        )
    output = np.asarray(output, dtype=float)
    return output.reshape(-1, 1) if output.ndim == 1 else output


def _simulate_transfer_acceleration(
    model: TransferFunctionModelSpec | StateSpaceModelSpec,
    time_s: np.ndarray,
    inputs: np.ndarray,
) -> np.ndarray | None:
    """Return the exact continuous-time output acceleration when the TF permits it."""

    if not isinstance(model, TransferFunctionModelSpec):
        return None
    if model.time_domain != "continuous" or inputs.ndim != 1:
        return None
    delayed = inputs.copy()
    if model.input_delay_s > 0.0:
        delayed = np.interp(
            time_s - model.input_delay_s,
            time_s,
            inputs,
            left=float(inputs[0]),
            right=float(inputs[-1]),
        )
    a, b, c, d = signal.tf2ss(model.numerator, model.denominator)
    direct = np.asarray(d, dtype=float)
    first_input_term = np.asarray(c @ b, dtype=float)
    if np.max(np.abs(direct)) > 1e-12 or np.max(np.abs(first_input_term)) > 1e-12:
        return None
    _, _, states = signal.lsim(
        signal.StateSpace(a, b, c, d),
        U=delayed,
        T=time_s,
    )
    state_rows = np.asarray(states, dtype=float)
    if state_rows.ndim == 1:
        state_rows = state_rows.reshape(-1, 1)
    state_term = np.asarray(c @ a @ a, dtype=float).reshape(-1)
    input_term = float(np.asarray(c @ a @ b, dtype=float).reshape(-1)[0])
    return state_rows @ state_term + delayed * input_term


def _pulse_output_signal_name(
    model: TransferFunctionModelSpec | StateSpaceModelSpec,
) -> str:
    """Describe the simulated model output honestly so the extractor can derive acceleration."""

    if isinstance(model, TransferFunctionModelSpec):
        signal_id = model.output_signal_id
        unit = model.output_units
    else:
        signal_id = model.output_signal_ids[0]
        unit = model.signal_units.get(signal_id, "")
    normalized_name = signal_id.replace("_", " ").replace("-", " ").lower()
    normalized_unit = unit.replace("²", "^2").replace(" ", "")
    if "acceleration" in normalized_name or "/s^2" in normalized_unit:
        return "acceleration"
    if any(token in normalized_name for token in ("speed", "velocity", "rate")):
        return "speed"
    if normalized_unit in {"m/s", "rad/s"}:
        return "speed"
    return "position"


def _registered_params(model: RegisteredNonlinearModelSpec, cls):
    allowed = {item.name for item in fields(cls)}
    unknown = set(model.parameters) - allowed
    missing = {
        item.name
        for item in fields(cls)
        if item.default is MISSING
        and item.default_factory is MISSING
        and item.name not in model.parameters
    }
    if unknown:
        raise ValueError(
            f"unknown {model.template_id} parameter(s): {', '.join(sorted(unknown))}"
        )
    if missing:
        raise ValueError(
            f"missing {model.template_id} parameter(s): {', '.join(sorted(missing))}"
        )
    return cls(**model.parameters)


def _run_registered_experiments(
    package: PlantEvidencePackage,
    plan: ExperimentPlan,
) -> list[SimulationExperimentRecord]:
    model = package.model
    assert isinstance(model, RegisteredNonlinearModelSpec)
    records: list[SimulationExperimentRecord] = []
    if model.template_id == "underactuated_cartpole":
        params = _registered_params(model, CartpoleParams)
        for instruction in plan.instructions:
            if str(instruction.primitive) != ExperimentPrimitive.FREE_DECAY.value:
                continue
            time_s, response = modal_trace(
                params.free_cart_natural_frequency_down_rad_s,
                0.08,
                duration_s=instruction.duration_s,
                sample_count=max(
                    101, int(instruction.duration_s * instruction.sample_rate_hz)
                ),
            )
            records.append(
                _model_record(package, instruction, time_s, {"free_response": response})
            )
    elif model.template_id == "vtol_cascaded":
        params = _registered_params(model, VtolParams)
        for instruction in plan.instructions:
            primitive = str(instruction.primitive)
            if primitive == ExperimentPrimitive.HOVER_THRUST.value:
                time_s, thrust, lift = hover_trace(params.hover_thrust_n)
                records.append(
                    _model_record(
                        package,
                        instruction,
                        time_s,
                        {"thrust": thrust, "lift": lift},
                    )
                )
            elif primitive == ExperimentPrimitive.PULSE.value:
                time_s, command, angular, tilt, lateral = vtol_pulse_trace(
                    1.0 / params.pitch_inertia_kg_m2,
                    params.gravity_m_s2,
                )
                records.append(
                    _model_record(
                        package,
                        instruction,
                        time_s,
                        {
                            "input": command,
                            "angular_acceleration": angular,
                            "tilt": tilt,
                            "coupled_output": lateral,
                        },
                    )
                )
    return records


def _model_record(
    package: PlantEvidencePackage,
    instruction,
    time_s: np.ndarray,
    signals: dict[str, np.ndarray],
) -> SimulationExperimentRecord:
    model = package.model
    signal_units: dict[str, str] = {}
    if isinstance(model, TransferFunctionModelSpec):
        input_unit = model.input_units
        output_unit = model.output_units
    elif isinstance(model, StateSpaceModelSpec):
        input_id = model.input_signal_ids[0]
        output_id = model.output_signal_ids[0]
        input_unit = model.signal_units.get(input_id, "input")
        output_unit = model.signal_units.get(output_id, "output")
    else:
        input_unit = ""
        output_unit = ""
    for signal_name in signals:
        if signal_name == "input" and input_unit:
            signal_units[signal_name] = input_unit
        elif signal_name in {"acceleration", "angular_acceleration"} and output_unit:
            signal_units[signal_name] = (
                output_unit
                if "/s^2" in output_unit.replace("²", "^2")
                else f"{output_unit}/s^2"
            )
        elif signal_name in {"speed", "velocity", "motion_rate"} and output_unit:
            signal_units[signal_name] = (
                output_unit
                if output_unit.replace(" ", "").endswith("/s")
                else f"{output_unit}/s"
            )
        elif signal_name in {"position", "free_response", "output"} and output_unit:
            signal_units[signal_name] = output_unit
    return SimulationExperimentRecord(
        plant_id=package.plant_id,
        evidence_package_id=package.evidence_package_id,
        model_sha256=hashlib.sha256(
            package.model.model_dump_json().encode()
        ).hexdigest(),
        evidence_source="model_simulation",
        primitive=instruction.primitive,
        estimates=instruction.estimates,
        instruction_title=instruction.title,
        repeat_index=1,
        experiment_protocol_version="user-model-v1",
        operating_region=instruction.operating_region
        or "declared_model_operating_region",
        evidence_boundary="user_object_model_simulation",
        trace=ExperimentTrace(
            time_s=np.asarray(time_s, dtype=float).tolist(),
            signals={
                name: np.asarray(values, dtype=float).tolist()
                for name, values in signals.items()
            },
            metadata={
                "model_kind": package.model.kind,
                "signal_units": signal_units,
            },
        ),
    )


def run_model_experiments(
    package: PlantEvidencePackage,
    plan: ExperimentPlan,
) -> list[SimulationExperimentRecord]:
    if package.model is None:
        return []
    if isinstance(package.model, RegisteredNonlinearModelSpec):
        return _run_registered_experiments(package, plan)
    model = package.model
    records: list[SimulationExperimentRecord] = []
    for instruction in plan.instructions:
        time_s, amplitude = _instruction_time(instruction, model)
        primitive = str(instruction.primitive)
        input_count = (
            1
            if isinstance(model, TransferFunctionModelSpec)
            else len(model.input_signal_ids)
        )
        inputs = np.zeros((len(time_s), input_count), dtype=float)
        start = max(1, len(time_s) // 10)
        if primitive == ExperimentPrimitive.RAMP_STEP.value:
            inputs[start:, 0] = amplitude
        elif primitive == ExperimentPrimitive.PULSE.value:
            width = max(2, len(time_s) // 20)
            inputs[start : start + width, 0] = amplitude
        elif primitive == ExperimentPrimitive.FREE_DECAY.value:
            width = max(2, len(time_s) // 100)
            inputs[start : start + width, 0] = amplitude
        elif primitive == ExperimentPrimitive.BOUNDED_SCAN.value:
            if input_count < 2:
                raise ValueError("bounded MIMO scan requires at least two model inputs")
            width = max(2, len(time_s) // 5)
            inputs[start : start + width, 0] = amplitude
            second_start = min(len(time_s) - width, 3 * len(time_s) // 5)
            inputs[second_start : second_start + width, 1] = amplitude
        else:
            raise ValueError(
                f"model adapter does not implement experiment primitive '{primitive}'"
            )
        model_input = inputs[:, 0] if input_count == 1 else inputs
        outputs = _simulate_linear(model, time_s, model_input)
        if primitive == ExperimentPrimitive.RAMP_STEP.value:
            signal_map = {"input": inputs[:, 0], "output": outputs[:, 0]}
        elif primitive == ExperimentPrimitive.FREE_DECAY.value:
            signal_map = {"free_response": outputs[:, 0]}
        elif primitive == ExperimentPrimitive.PULSE.value:
            acceleration = _simulate_transfer_acceleration(model, time_s, model_input)
            signal_map = {
                "input": inputs[:, 0],
                (
                    "acceleration"
                    if acceleration is not None
                    else _pulse_output_signal_name(model)
                ): acceleration if acceleration is not None else outputs[:, 0],
            }
        else:
            signal_map = {
                **{f"input_{index + 1}": inputs[:, index] for index in range(2)},
                **{f"output_{index + 1}": outputs[:, index] for index in range(2)},
            }
        records.append(_model_record(package, instruction, time_s, signal_map))
    return records
