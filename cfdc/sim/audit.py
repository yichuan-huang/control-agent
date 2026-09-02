"""Independent, protocol-bound providers for the public CFDC audit cases.

The numerical plants in this module are private implementation details.  The
only cross-boundary values are protocol-bound :class:`PublicTrace` instances
and sampled evaluation trials.  In particular, this module deliberately does
not import routing, controller synthesis, legacy archives, or historical
result logs.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import signal

from cfdc.experiments.operator import expected_input_waveforms
from cfdc.kernel.contracts import PROTOCOL_VERSION, fingerprint
from cfdc.kernel.providers import (
    EvaluationProviderRegistry,
    ProviderRegistry,
    PublicTrace,
)

# Never serialize this mapping into an artifact, trace, provider attestation,
# prompt, or download.  Case names are public; model parameters are not.
_PRIVATE_MODELS: dict[str, dict[str, Any]] = {
    "audit_class_i_level": {
        "family": "first_order",
        "gain": 1.18,
        "tau": 2.15,
        "delay": 0.05,
        "noise": 0.0035,
    },
    "audit_class_ii_thermal": {
        "family": "two_lag_delay",
        "gain": 1.25,
        "tau1": 2.35,
        "tau2": 0.58,
        "delay": 0.24,
        "noise": 0.004,
    },
    "audit_class_ii_oscillator": {
        "family": "underdamped",
        "gain": 1.05,
        "wn": 1.35,
        "zeta": 0.34,
        "delay": 0.02,
        "noise": 0.003,
    },
    "audit_class_iii_motion": {
        "family": "damped_integrator",
        "gain": 0.88,
        "drag": 0.30,
        "delay": 0.0,
        "noise": 0.003,
    },
    "audit_class_iv_nmp": {
        "family": "stable_nmp",
        "gain": 1.08,
        "wn": 1.45,
        "zeta": 0.68,
        "zero": 1.05,
        "delay": 0.0,
        "noise": 0.0035,
    },
    "audit_class_iv_high_order": {
        "family": "three_real_lags",
        "gain": 1.0,
        "tau1": 2.4,
        "tau2": 1.0,
        "tau3": 0.45,
        "delay": 0.0,
        "noise": 0.0025,
    },
    "audit_class_v_mimo": {
        "family": "mimo",
        "matrix": [[1.12, 0.055], [0.045, 0.92]],
        "taus": [[0.9, 0.75], [0.82, 1.1]],
        "noise": 0.0015,
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


def _delay(values: np.ndarray, time_s: np.ndarray, delay_s: float) -> np.ndarray:
    return np.interp(time_s - delay_s, time_s, values, left=values[0])


def _siso_response(
    model: Mapping[str, Any], time_s: np.ndarray, command: np.ndarray
) -> np.ndarray:
    family = str(model["family"])
    if family == "first_order":
        numerator, denominator = [model["gain"]], [model["tau"], 1.0]
    elif family == "two_lag_delay":
        numerator, denominator = (
            [model["gain"]],
            [model["tau1"] * model["tau2"], model["tau1"] + model["tau2"], 1.0],
        )
    elif family == "underdamped":
        numerator, denominator = (
            [model["gain"] * model["wn"] ** 2],
            [1.0, 2.0 * model["zeta"] * model["wn"], model["wn"] ** 2],
        )
    elif family == "damped_integrator":
        numerator, denominator = [model["gain"]], [1.0, model["drag"], 0.0]
    elif family == "stable_nmp":
        numerator, denominator = (
            [-model["gain"] / model["zero"], model["gain"]],
            [1.0 / model["wn"] ** 2, 2.0 * model["zeta"] / model["wn"], 1.0],
        )
    elif family == "three_real_lags":
        numerator, denominator = (
            [model["gain"]],
            [
                model["tau1"] * model["tau2"] * model["tau3"],
                model["tau1"] * model["tau2"]
                + model["tau1"] * model["tau3"]
                + model["tau2"] * model["tau3"],
                model["tau1"] + model["tau2"] + model["tau3"],
                1.0,
            ],
        )
    else:
        raise ValueError("audit_provider_siso_model_invalid")
    _, output, _ = signal.lsim(
        signal.TransferFunction(numerator, denominator),
        U=_delay(command, time_s, float(model.get("delay", 0.0))),
        T=time_s,
    )
    return np.asarray(output, dtype=float)


def _validate_scope(operation: Mapping[str, Any], task: Mapping[str, Any]) -> None:
    if operation.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("audit_provider_requires_compiled_protocol")
    if str(operation.get("task_fingerprint") or "") != str(
        task.get("task_fingerprint") or ""
    ):
        raise ValueError("audit_provider_task_scope_mismatch")
    expected_outputs = {str(item) for item in operation.get("requested_signals", ())}
    task_outputs = {str(item) for item in task.get("measured_signals", ())}
    expected_inputs = {str(item) for item in operation.get("control_inputs", ())}
    task_inputs = {
        str(item) for item in task.get("control_inputs") or (task.get("control_input"),)
    }
    if expected_outputs != task_outputs or expected_inputs != task_inputs:
        raise ValueError("audit_provider_task_scope_mismatch")


@dataclass
class AuditExperimentProvider:
    """Execute public, repeated traces against one private audit model."""

    case_id: str
    seed: int = 27181
    provider_version: str = "cfdc-audit-experiment/v1"
    capabilities: frozenset[str] = _CAPABILITIES

    def __post_init__(self) -> None:
        if self.case_id not in _PRIVATE_MODELS:
            raise ValueError(f"unknown_audit_case: {self.case_id}")

    @property
    def provider_id(self) -> str:
        return f"cfdc-audit-experiment:{self.case_id}"

    def execute(
        self, operation: Mapping[str, Any], *, task: Mapping[str, Any]
    ) -> tuple[PublicTrace, ...]:
        _validate_scope(operation, task)
        model = _PRIVATE_MODELS[self.case_id]
        time_s, commands = expected_input_waveforms(operation)
        inputs = tuple(str(item) for item in operation["control_inputs"])
        outputs = tuple(str(item) for item in operation["requested_signals"])
        rng = np.random.default_rng(self.seed)
        traces: list[PublicTrace] = []
        for repeat in range(int(operation["repeats"])):
            signals: dict[str, tuple[float, ...]] = {
                "input": tuple(float(value) for value in commands[inputs[0]])
            }
            unit_map = {
                "input": str(operation["units"]["input"]),
                **{
                    str(name): str(unit)
                    for name, unit in operation["units"]["outputs"].items()
                },
            }
            for name in inputs:
                signals[name] = tuple(float(value) for value in commands[name])
                unit_map[name] = str(operation["units"]["input"])
            if model["family"] == "mimo":
                matrix = np.asarray(model["matrix"], dtype=float)
                taus = np.asarray(model["taus"], dtype=float)
                for row, output_name in enumerate(outputs):
                    value = np.zeros_like(time_s)
                    for column, input_name in enumerate(inputs):
                        _, partial, _ = signal.lsim(
                            signal.TransferFunction(
                                [matrix[row, column]], [taus[row, column], 1.0]
                            ),
                            U=commands[input_name],
                            T=time_s,
                        )
                        value += partial
                    signals[output_name] = tuple(
                        float(item)
                        for item in value + rng.normal(0.0, model["noise"], len(time_s))
                    )
            else:
                value = _siso_response(model, time_s, commands[inputs[0]])
                signals[outputs[0]] = tuple(
                    float(item)
                    for item in value + rng.normal(0.0, model["noise"], len(time_s))
                )
            traces.append(
                PublicTrace(
                    trace_id=f"audit-trace-{self.case_id}-{repeat + 1:02d}",
                    source="demo_fixture",
                    time_s=tuple(float(item) for item in time_s),
                    signals=signals,
                    units=unit_map,
                    protocol_fingerprint=str(operation["protocol_fingerprint"]),
                    operating_region=str(
                        task.get("operating_region") or "declared_region"
                    ),
                    trial_id=f"repeat-{repeat + 1:02d}",
                    metadata={
                        "audit_case_id": self.case_id,
                        "public_evidence_scope": "protocol_bound_measurement",
                        "control_inputs": list(inputs),
                        "measured_signals": list(outputs),
                        "public_artifact_fingerprint": fingerprint(
                            {
                                "case_id": self.case_id,
                                "repeat": repeat + 1,
                                "protocol": operation["protocol_fingerprint"],
                            }
                        ),
                    },
                )
            )
        return tuple(traces)


@dataclass
class AuditEvaluationProvider:
    """Run perturbed sampled evaluation without disclosing plant parameters."""

    case_id: str
    provider_version: str = "cfdc-audit-evaluation/v1"
    capabilities: frozenset[str] = frozenset(
        {"software_evaluation", "perturbed_repeats", "multistage", "disturbance"}
    )

    def __post_init__(self) -> None:
        if self.case_id not in _PRIVATE_MODELS:
            raise ValueError(f"unknown_audit_case: {self.case_id}")

    @property
    def provider_id(self) -> str:
        return f"cfdc-audit-evaluation:{self.case_id}"

    def evaluate(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        from cfdc.kernel.execution_contract import EXECUTION_VERSION
        from cfdc.sim.execution import simulate_trial

        if request.get("request_version") != EXECUTION_VERSION:
            raise ValueError("evaluation_execution_request_required")
        trials = [
            simulate_trial(
                request,
                scenario,
                _evaluation_plant(self.case_id, request, int(scenario["seed"])),
            )
            for scenario in request["trials"]
        ]
        return {
            "evaluation_split": request["evaluation_split"],
            "trials": trials,
            "provider_attestation": {
                "audit_case_id": self.case_id,
                "scope": "independent sampled software execution",
                "parameter_disclosure": "none",
            },
            "private_truth_returned": False,
        }


def _evaluation_plant(case_id: str, request: Mapping[str, Any], seed: int):
    """Build a perturbed private plant for the execution-only evaluator."""
    from cfdc.sim.execution import LinearPlant

    model = _PRIVATE_MODELS[case_id]
    inputs = tuple(str(item) for item in request["control_inputs"])
    outputs = tuple(str(item) for item in request["tracked_signals"])
    rng = np.random.default_rng(seed)
    gain_scale, time_scale = rng.uniform(0.96, 1.04, 2)
    if model["family"] == "mimo":
        matrix = [
            [
                (
                    [float(model["matrix"][row][column] * gain_scale)],
                    [float(model["taus"][row][column] * time_scale), 1.0],
                )
                for column in range(2)
            ]
            for row in range(2)
        ]
        return LinearPlant.from_transfer_matrix(matrix, inputs=inputs, outputs=outputs)
    family = str(model["family"])
    gain = float(model["gain"] * gain_scale)
    if family == "first_order":
        numerator, denominator = [gain], [float(model["tau"] * time_scale), 1.0]
    elif family == "two_lag_delay":
        tau1, tau2 = model["tau1"] * time_scale, model["tau2"] * time_scale
        numerator, denominator = [gain], [tau1 * tau2, tau1 + tau2, 1.0]
    elif family == "underdamped":
        wn = model["wn"] / time_scale
        numerator, denominator = [gain * wn**2], [1.0, 2.0 * model["zeta"] * wn, wn**2]
    elif family == "damped_integrator":
        numerator, denominator = [gain], [1.0, float(model["drag"] / time_scale), 0.0]
    elif family == "stable_nmp":
        wn = model["wn"] / time_scale
        numerator, denominator = (
            [-gain / model["zero"], gain],
            [1.0 / wn**2, 2.0 * model["zeta"] / wn, 1.0],
        )
    elif family == "three_real_lags":
        tau1, tau2, tau3 = (
            model["tau1"] * time_scale,
            model["tau2"] * time_scale,
            model["tau3"] * time_scale,
        )
        numerator, denominator = (
            [gain],
            [
                tau1 * tau2 * tau3,
                tau1 * tau2 + tau1 * tau3 + tau2 * tau3,
                tau1 + tau2 + tau3,
                1.0,
            ],
        )
    else:
        raise ValueError("audit_evaluation_plant_unregistered")
    return LinearPlant.from_transfer_matrix(
        [[(numerator, denominator)]],
        inputs=inputs,
        outputs=outputs,
        delays={inputs[0]: float(model.get("delay", 0.0))},
    )


def build_audit_provider_registries(
    case_id: str,
) -> tuple[ProviderRegistry, str, EvaluationProviderRegistry, str]:
    """Build isolated identification and evaluation registries for one audit."""
    identification = AuditExperimentProvider(case_id)
    evaluation = AuditEvaluationProvider(case_id)
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
    "AuditEvaluationProvider",
    "AuditExperimentProvider",
    "build_audit_provider_registries",
]
