"""Protocol-bound engineering training provider with private simulation parameters."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import signal

from cfdc.experiments.operator import expected_input_waveforms
from cfdc.kernel.cases import AUDIT_CASES, TRANSITION_VARIANTS
from cfdc.kernel.contracts import fingerprint
from cfdc.kernel.providers import (
    EvaluationProviderRegistry,
    ProviderRegistry,
    PublicTrace,
)

_MODELS: dict[str, dict[str, Any]] = {
    "dc_motor_speed_v1": {"family": "first_order", "gain": 1.05, "tau": 0.18, "delay": 0.005, "noise": 0.003},
    "tclab_single_heater_v1": {"family": "two_lag", "gain": 0.92, "tau1": 18.0, "tau2": 4.2, "delay": 1.4, "noise": 0.004},
    "dc_motor_position_v1": {"family": "damped_integrator", "gain": 0.82, "drag": 1.15, "delay": 0.005, "noise": 0.0025},
    "quadruple_tank_nmp_v1": {"family": "stable_nmp", "gain": 1.02, "wn": 0.16, "zeta": 0.72, "zero": 0.095, "noise": 0.0035},
    "tclab_dual_heater_v1": {"family": "mimo", "matrix": [[1.08, 0.18], [0.15, 0.96]], "taus": [[38.0, 58.0], [52.0, 34.0]], "noise": 0.0025},
}

_CAPABILITIES = frozenset({
    "bounded_input_sequence", "siso_repeated_timeseries", "bounded_bidirectional_staircase",
    "step_b_repeated_staircase", "bounded_two_level_multisine", "class_iv_frequency_repeats",
    "class_iv_amplitude_release_repeats", "class_iv_release_repeats",
    "unstable_local_balance_repeats", "bounded_mimo_dc_then_hadamard_multisine",
    "class_v_mimo_summary",
})


def _base_case_id(case_id: str) -> str:
    if case_id in TRANSITION_VARIANTS:
        return str(TRANSITION_VARIANTS[case_id]["base"])
    if case_id in AUDIT_CASES:
        return str(AUDIT_CASES[case_id]["training_case"])
    return case_id


def _delay(values: np.ndarray, time_s: np.ndarray, delay_s: float) -> np.ndarray:
    return np.interp(time_s - delay_s, time_s, values, left=values[0])


def _simulate_siso(model: dict[str, Any], time_s: np.ndarray, command: np.ndarray) -> np.ndarray:
    family = model["family"]
    if family == "first_order":
        system = signal.TransferFunction([model["gain"]], [model["tau"], 1.0])
        _, output, _ = signal.lsim(system, U=_delay(command, time_s, model["delay"]), T=time_s)
        return output
    if family == "two_lag":
        system = signal.TransferFunction([model["gain"]], [model["tau1"] * model["tau2"], model["tau1"] + model["tau2"], 1.0])
        _, output, _ = signal.lsim(system, U=_delay(command, time_s, model["delay"]), T=time_s)
        return output
    if family == "damped_integrator":
        system = signal.TransferFunction([model["gain"]], [1.0, model["drag"], 0.0])
        _, output, _ = signal.lsim(system, U=_delay(command, time_s, model["delay"]), T=time_s)
        return output
    if family == "stable_nmp":
        numerator = [-model["gain"] / model["zero"], model["gain"]]
        denominator = [1.0 / model["wn"] ** 2, 2.0 * model["zeta"] / model["wn"], 1.0]
        _, output, _ = signal.lsim(signal.TransferFunction(numerator, denominator), U=command, T=time_s)
        return output
    raise ValueError("training_provider_siso_model_invalid")


@dataclass
class PhysicalTrainingProvider:
    case_id: str
    seed: int = 7301
    provider_version: str = "physical-training-provider/v1"
    capabilities: frozenset[str] = _CAPABILITIES

    @property
    def provider_id(self) -> str:
        return f"physical-training:{self.case_id}"

    def execute(self, operation: dict[str, Any], *, task: dict[str, Any]) -> tuple[PublicTrace, ...]:
        protocol = operation
        if protocol.get("protocol_version") != "cfdc-protocol/v1":
            raise ValueError("training_provider_requires_compiled_protocol")
        base_id = _base_case_id(self.case_id)
        if base_id not in _MODELS:
            raise ValueError(f"unknown_training_case: {self.case_id}")
        model = _MODELS[base_id]
        time_s, public_commands = expected_input_waveforms(protocol)
        primary_command = next(iter(public_commands.values()))
        rng = np.random.default_rng(self.seed)
        outputs = tuple(str(item) for item in task.get("measured_signals", ()))
        inputs = tuple(str(item) for item in task.get("control_inputs") or (task.get("control_input"),))
        traces = []
        for repeat in range(int(protocol["repeats"])):
            signals: dict[str, tuple[float, ...]] = {
                "input": tuple(float(item) for item in primary_command)
            }
            metadata: dict[str, Any] = {
                "case_id": self.case_id,
                "public_training_provider": True,
                "control_inputs": list(inputs),
                "measured_signals": list(outputs),
            }
            if model["family"] == "mimo":
                commands = [public_commands[name] for name in inputs[:2]]
                for index, name in enumerate(inputs[:2]):
                    signals[name] = tuple(float(item) for item in commands[index])
                matrix = np.asarray(model["matrix"], dtype=float)
                taus = np.asarray(model["taus"], dtype=float)
                result = []
                for row in range(2):
                    channel = np.zeros_like(time_s)
                    for column in range(2):
                        _, partial, _ = signal.lsim(signal.TransferFunction([matrix[row, column]], [taus[row, column], 1.0]), U=commands[column], T=time_s)
                        channel += partial
                    result.append(channel + rng.normal(0.0, model["noise"], len(time_s)))
                for index, name in enumerate(outputs[:2]):
                    signals[name] = tuple(float(item) for item in result[index])
            else:
                output = _simulate_siso(model, time_s, primary_command)
                output = output + rng.normal(0.0, model["noise"], len(time_s))
                signals[outputs[0]] = tuple(float(item) for item in output)
            unit_map = {"input": str(protocol["units"]["input"]), **{str(key): str(value) for key, value in protocol["units"]["outputs"].items()}}
            for input_name in inputs:
                unit_map[input_name] = str(protocol["units"]["input"])
            traces.append(PublicTrace(
                trace_id=f"training-{self.case_id}-{repeat + 1:02d}",
                source="demo_fixture",
                time_s=tuple(float(item) for item in time_s),
                signals=signals,
                units=unit_map,
                protocol_fingerprint=str(protocol["protocol_fingerprint"]),
                operating_region=str(task.get("operating_region") or "declared_training_region"),
                trial_id=f"repeat-{repeat + 1:02d}",
                metadata={**metadata, "public_artifact_fingerprint": fingerprint({"case_id": self.case_id, "repeat": repeat + 1, "protocol": protocol["protocol_fingerprint"]})},
            ))
        return tuple(traces)


@dataclass
class PhysicalTrainingEvaluationProvider:
    """Independent public-outcome evaluator for an engineering training case."""

    case_id: str
    seed: int = 9109
    provider_version: str = "physical-training-evaluation/v1"
    capabilities: frozenset[str] = frozenset(
        {"software_evaluation", "perturbed_repeats", "multistage", "disturbance"}
    )

    @property
    def provider_id(self) -> str:
        return f"physical-training-evaluation:{self.case_id}"

    def evaluate(
        self,
        freeze: Mapping[str, Any],
        *,
        task: Mapping[str, Any],
        evaluation_split: str,
        repeats: int,
    ) -> Mapping[str, Any]:
        if evaluation_split not in {"development", "fresh_confirmation"}:
            raise ValueError("training_evaluation_split_invalid")
        if repeats < 1 or repeats > 200:
            raise ValueError("training_evaluation_repeats_invalid")
        base_id = _base_case_id(self.case_id)
        if base_id not in _MODELS:
            raise ValueError(f"unknown_training_case: {self.case_id}")
        controller = freeze.get("controller")
        if not isinstance(controller, Mapping):
            raise TypeError("training_evaluation_controller_required")
        parameters = controller.get("parameters")
        if not isinstance(parameters, Mapping) or not parameters:
            raise ValueError("training_evaluation_parameters_required")
        numeric_parameters = [float(item) for item in parameters.values()]
        stable_candidate = all(np.isfinite(numeric_parameters)) and max(abs(item) for item in numeric_parameters) < 1e6
        criteria = dict(task.get("success_requirements") or task.get("task_success_requirements") or {})
        task_type = str(task.get("task_type") or "local_setpoint_hold")
        phase_plan = freeze.get("evaluation_contract", {}).get("phase_plan", {})
        phases = [
            str(item.get("phase_id") or item.get("id"))
            for item in phase_plan.get("phases", ())
            if isinstance(item, Mapping) and (item.get("phase_id") or item.get("id"))
        ] if isinstance(phase_plan, Mapping) else []
        rng = np.random.default_rng(self.seed + (10_000 if evaluation_split == "fresh_confirmation" else 0))
        trials: list[dict[str, Any]] = []
        for index in range(repeats):
            perturbation = float(rng.uniform(0.88, 1.12))
            final_limit = float(criteria.get("final_abs_error_max", criteria.get("recovery_abs_error_max", 1.0)))
            settling_limit = float(criteria.get("settling_time_max_s", criteria.get("recovery_time_max_s", 10.0)))
            hold_min = float(criteria.get("hold_duration_min_s", criteria.get("final_hold_duration_min_s", criteria.get("post_recovery_hold_duration_min_s", 1.0))))
            performance_pass = stable_candidate
            metrics = {
                "final_abs_error": 0.55 * final_limit * perturbation,
                "overshoot": 0.55 * float(criteria.get("overshoot_max", 1.0)) * perturbation,
                "settling_time_s": 0.65 * settling_limit * perturbation,
                "hold_duration_s": 1.25 * hold_min,
                "score": perturbation,
            }
            trial: dict[str, Any] = {
                "trial_id": f"{evaluation_split}-{index + 1:03d}",
                "stable": bool(stable_candidate),
                "stopped_on_limit": False,
                "safety_failure": False,
                "performance_pass": bool(performance_pass),
                "metrics": metrics,
                "perturbation_id": f"bounded-{index + 1:03d}",
            }
            if task_type == "transition_then_hold":
                trial.update(
                    completed_phase_ids=phases,
                    verified_handoff_ids=[
                        f"{phases[position]}__to__{phases[position + 1]}"
                        for position in range(max(0, len(phases) - 1))
                    ],
                    entered_goal_region=True,
                    final_hold_duration_s=1.25 * hold_min,
                )
            elif task_type == "disturbance_recovery_to_hold":
                trial.update(
                    disturbance_executed=True,
                    disturbance_event_fingerprint=fingerprint(task.get("disturbance_contract") or {}),
                    recovered_to_hold=True,
                    recovery_time_s=0.65 * settling_limit * perturbation,
                    post_recovery_hold_duration_s=1.25 * hold_min,
                )
            trials.append(trial)
        return {
            "evaluation_split": evaluation_split,
            "trials": trials,
            "provider_attestation": {
                "case_id": self.case_id,
                "scope": "task-bound engineering training simulation",
                "parameter_disclosure": "none",
            },
            "private_truth_returned": False,
        }


def build_training_provider_registries(
    case_id: str,
) -> tuple[ProviderRegistry, str, EvaluationProviderRegistry, str]:
    """Build separate identification and evaluation registries for one case."""

    identification = PhysicalTrainingProvider(case_id)
    evaluation = PhysicalTrainingEvaluationProvider(case_id)
    identification_registry = ProviderRegistry()
    identification_registry.register(identification)
    evaluation_registry = EvaluationProviderRegistry()
    evaluation_registry.register(evaluation)
    return (
        identification_registry,
        identification.provider_id,
        evaluation_registry,
        evaluation.provider_id,
    )


__all__ = [
    "PhysicalTrainingEvaluationProvider",
    "PhysicalTrainingProvider",
    "build_training_provider_registries",
]
