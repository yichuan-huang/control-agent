"""Protocol-bound engineering training provider with private simulation parameters."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import signal

from cfdc.experiments.operator import expected_input_waveforms
from cfdc.kernel.cases import AUDIT_CASES, TRANSITION_VARIANTS
from cfdc.kernel.contracts import PROTOCOL_VERSION, fingerprint
from cfdc.kernel.providers import (
    EvaluationProviderRegistry,
    ProviderRegistry,
    PublicTrace,
)

_MODELS: dict[str, dict[str, Any]] = {
    "dc_motor_speed_v1": {
        "family": "first_order",
        "gain": 1.05,
        "tau": 0.18,
        "delay": 0.005,
        "noise": 0.003,
    },
    "tclab_single_heater_v1": {
        "family": "two_lag",
        "gain": 0.92,
        "tau1": 18.0,
        "tau2": 4.2,
        "delay": 1.4,
        "noise": 0.004,
    },
    "dc_motor_position_v1": {
        "family": "damped_integrator",
        "gain": 0.82,
        "drag": 1.15,
        "delay": 0.005,
        "noise": 0.0025,
    },
    "quadruple_tank_nmp_v1": {
        "family": "stable_nmp",
        "gain": 1.02,
        "wn": 0.16,
        "zeta": 0.72,
        "zero": 0.095,
        "noise": 0.0035,
    },
    "tclab_dual_heater_v1": {
        "family": "mimo",
        "matrix": [[1.08, 0.18], [0.15, 0.96]],
        "taus": [[38.0, 58.0], [52.0, 34.0]],
        "noise": 0.0025,
    },
}

_CAPABILITIES = frozenset(
    {
        "bounded_input_sequence",
        "siso_repeated_timeseries",
        "bounded_bidirectional_staircase",
        "step_b_repeated_staircase",
        "bounded_two_level_multisine",
        "class_iv_frequency_repeats",
        "class_iv_amplitude_release_repeats",
        "class_iv_release_repeats",
        "unstable_local_balance_repeats",
        "bounded_mimo_dc_then_hadamard_multisine",
        "class_v_mimo_summary",
    }
)


def _base_case_id(case_id: str) -> str:
    if case_id in TRANSITION_VARIANTS:
        return str(TRANSITION_VARIANTS[case_id]["base"])
    return case_id


def _delay(values: np.ndarray, time_s: np.ndarray, delay_s: float) -> np.ndarray:
    return np.interp(time_s - delay_s, time_s, values, left=values[0])


def _simulate_siso(
    model: dict[str, Any], time_s: np.ndarray, command: np.ndarray
) -> np.ndarray:
    family = model["family"]
    if family == "first_order":
        system = signal.TransferFunction([model["gain"]], [model["tau"], 1.0])
        _, output, _ = signal.lsim(
            system, U=_delay(command, time_s, model["delay"]), T=time_s
        )
        return output
    if family == "two_lag":
        system = signal.TransferFunction(
            [model["gain"]],
            [model["tau1"] * model["tau2"], model["tau1"] + model["tau2"], 1.0],
        )
        _, output, _ = signal.lsim(
            system, U=_delay(command, time_s, model["delay"]), T=time_s
        )
        return output
    if family == "damped_integrator":
        system = signal.TransferFunction([model["gain"]], [1.0, model["drag"], 0.0])
        _, output, _ = signal.lsim(
            system, U=_delay(command, time_s, model["delay"]), T=time_s
        )
        return output
    if family == "stable_nmp":
        numerator = [-model["gain"] / model["zero"], model["gain"]]
        denominator = [1.0 / model["wn"] ** 2, 2.0 * model["zeta"] / model["wn"], 1.0]
        _, output, _ = signal.lsim(
            signal.TransferFunction(numerator, denominator), U=command, T=time_s
        )
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

    def execute(
        self, operation: dict[str, Any], *, task: dict[str, Any]
    ) -> tuple[PublicTrace, ...]:
        protocol = operation
        if protocol.get("protocol_version") != PROTOCOL_VERSION:
            raise ValueError("training_provider_requires_compiled_protocol")
        base_id = _base_case_id(self.case_id)
        if base_id not in _MODELS:
            raise ValueError(f"unknown_training_case: {self.case_id}")
        model = _MODELS[base_id]
        time_s, public_commands = expected_input_waveforms(protocol)
        primary_command = next(iter(public_commands.values()))
        rng = np.random.default_rng(self.seed)
        outputs = tuple(str(item) for item in task.get("measured_signals", ()))
        inputs = tuple(
            str(item)
            for item in task.get("control_inputs") or (task.get("control_input"),)
        )
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
                        _, partial, _ = signal.lsim(
                            signal.TransferFunction(
                                [matrix[row, column]], [taus[row, column], 1.0]
                            ),
                            U=commands[column],
                            T=time_s,
                        )
                        channel += partial
                    result.append(
                        channel + rng.normal(0.0, model["noise"], len(time_s))
                    )
                for index, name in enumerate(outputs[:2]):
                    signals[name] = tuple(float(item) for item in result[index])
            else:
                output = _simulate_siso(model, time_s, primary_command)
                output = output + rng.normal(0.0, model["noise"], len(time_s))
                signals[outputs[0]] = tuple(float(item) for item in output)
            unit_map = {
                "input": str(protocol["units"]["input"]),
                **{
                    str(key): str(value)
                    for key, value in protocol["units"]["outputs"].items()
                },
            }
            for input_name in inputs:
                unit_map[input_name] = str(protocol["units"]["input"])
            traces.append(
                PublicTrace(
                    trace_id=f"training-{self.case_id}-{repeat + 1:02d}",
                    source="demo_fixture",
                    time_s=tuple(float(item) for item in time_s),
                    signals=signals,
                    units=unit_map,
                    protocol_fingerprint=str(protocol["protocol_fingerprint"]),
                    operating_region=str(
                        task.get("operating_region") or "declared_training_region"
                    ),
                    trial_id=f"repeat-{repeat + 1:02d}",
                    metadata={
                        **metadata,
                        "public_artifact_fingerprint": fingerprint(
                            {
                                "case_id": self.case_id,
                                "repeat": repeat + 1,
                                "protocol": protocol["protocol_fingerprint"],
                            }
                        ),
                    },
                )
            )
        return tuple(traces)


@dataclass
class PhysicalTrainingEvaluationProvider:
    """Independent public-outcome evaluator for an engineering training case."""

    case_id: str
    seed: int = 9109
    provider_version: str = "physical-training-evaluation/v2"
    capabilities: frozenset[str] = frozenset(
        {"software_evaluation", "perturbed_repeats", "multistage", "disturbance"}
    )

    @property
    def provider_id(self) -> str:
        return f"physical-training-evaluation:{self.case_id}"

    def evaluate(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        """Execute the frozen controller; no scoring contract enters the provider."""
        from cfdc.kernel.execution_contract import EXECUTION_VERSION
        from cfdc.sim.execution import simulate_trial

        if request.get("request_version") != EXECUTION_VERSION:
            raise ValueError("evaluation_execution_request_required")
        trials = []
        for scenario in request["trials"]:
            plant = _evaluation_plant(self.case_id, request, int(scenario["seed"]))
            trials.append(simulate_trial(request, scenario, plant))
        return {
            "evaluation_split": request["evaluation_split"],
            "trials": trials,
            "provider_attestation": {
                "case_id": self.case_id,
                "scope": "actual sampled software execution",
                "parameter_disclosure": "none",
            },
            "private_truth_returned": False,
        }


def _evaluation_plant(case_id: str, request: Mapping[str, Any], seed: int):
    """Private numerical factory; its parameters never leave the provider."""
    from cfdc.sim.execution import LinearPlant

    model = _MODELS[_base_case_id(case_id)]
    rng = np.random.default_rng(seed)
    gain_scale, time_scale = rng.uniform(0.97, 1.03, 2)
    family = model["family"]
    inputs = tuple(request["control_inputs"])
    outputs = tuple(request["tracked_signals"])
    delays = {}
    if family == "mimo":
        matrix = [
            [
                (
                    [float(model["matrix"][i][j] * gain_scale)],
                    [float(model["taus"][i][j] * time_scale), 1.0],
                )
                for j in range(2)
            ]
            for i in range(2)
        ]
    else:
        gain = float(model["gain"] * gain_scale)
        if family == "first_order":
            numerator, denominator = [gain], [float(model["tau"] * time_scale), 1.0]
        elif family == "two_lag":
            tau1, tau2 = model["tau1"] * time_scale, model["tau2"] * time_scale
            numerator, denominator = [gain], [tau1 * tau2, tau1 + tau2, 1.0]
        elif family == "damped_integrator":
            numerator, denominator = (
                [gain],
                [1.0, float(model["drag"] / time_scale), 0.0],
            )
        elif family == "stable_nmp":
            wn = model["wn"] / time_scale
            numerator, denominator = (
                [-gain / model["zero"], gain],
                [1 / wn**2, 2 * model["zeta"] / wn, 1.0],
            )
        else:
            raise ValueError("training_evaluation_plant_unregistered")
        matrix = [[(numerator, denominator)]]
        delays = {inputs[0]: float(model.get("delay", 0.0))}
    return LinearPlant.from_transfer_matrix(
        matrix, inputs=inputs, outputs=outputs, delays=delays
    )


def build_training_provider_registries(
    case_id: str,
) -> tuple[ProviderRegistry, str, EvaluationProviderRegistry, str]:
    """Build separate identification and evaluation registries for one case."""

    if case_id in AUDIT_CASES:
        # Audit dynamics live behind their own provider boundary.  Keep this
        # factory as the one registration entry point used by Kernel bindings.
        from cfdc.sim.audit import build_audit_provider_registries

        return build_audit_provider_registries(case_id)
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
