from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from cfdc.lab import PControllerSpec, RegisteredControllerSpec
from cfdc.models import TransferFunctionModelSpec
from cfdc.sim import run_linear_closed_loop


def lead_lag_controller(gain_scale: float = 1.0) -> RegisteredControllerSpec:
    return RegisteredControllerSpec(
        controller_id="fixed_lead_lag_cascade",
        parameters={"gain_scale": gain_scale},
    )


def discrete_lead_controller(
    gain_scale: float = 1.0,
) -> RegisteredControllerSpec:
    return RegisteredControllerSpec(
        controller_id="fixed_discrete_lead",
        parameters={"gain_scale": gain_scale},
    )


def test_registered_linear_snapshots_have_exact_deeply_immutable_keysets():
    lead_lag = lead_lag_controller()
    discrete = discrete_lead_controller()

    assert lead_lag.parameters == {"gain_scale": 1.0}
    assert discrete.parameters == {"gain_scale": 1.0}
    with pytest.raises(TypeError, match="immutable"):
        lead_lag.parameters["gain_scale"] = 2.0

    for payload in (
        {
            "controller_id": "fixed_lead_lag_cascade",
            "parameters": {"gain_scale": 1.0, "unknown": 1.0},
        },
        {
            "controller_id": "fixed_discrete_lead",
            "parameters": {},
            "reference": {"y": 0.0},
        },
    ):
        with pytest.raises(ValidationError, match="exact keys|exact key set"):
            RegisteredControllerSpec.model_validate(payload)


def test_fixed_lead_lag_runs_only_on_continuous_siso_and_is_stable():
    plant = TransferFunctionModelSpec(
        numerator=[1.0],
        denominator=[1.0, 1.0, 0.0],
        input_signal_id="u",
        output_signal_id="y",
    )
    result = run_linear_closed_loop(
        plant,
        lead_lag_controller(),
        reference=0.1,
        horizon_s=300.0,
        sample_time_s=0.02,
        actuator_bounds={"u": (-1.0, 1.0)},
        output_bounds={"y": (-1.25, 1.25)},
    )

    assert result.stability.status == "stable"
    assert max(pole.real for pole in result.stability.poles) == pytest.approx(
        -0.0907, abs=0.01
    )
    assert len(result.trace.time_s) == 15_001
    assert result.trace.requested_controls["u"] != result.trace.outputs["y"]

    discrete_plant = plant.model_copy(
        update={"time_domain": "discrete", "sample_time_s": 0.02}
    )
    with pytest.raises(ValueError, match="continuous plant"):
        run_linear_closed_loop(
            discrete_plant,
            lead_lag_controller(),
            reference=0.1,
            horizon_s=1.0,
            sample_time_s=0.02,
        )


def test_fixed_discrete_lead_uses_exact_z_realization_and_is_stable():
    plant = TransferFunctionModelSpec(
        numerator=[0.0003099120283325263, 0.000307340170959125],
        denominator=[1.0, -1.9753099120283326, 0.9753099120283326],
        time_domain="discrete",
        sample_time_s=0.025,
        input_signal_id="voltage",
        output_signal_id="position",
    )
    result = run_linear_closed_loop(
        plant,
        discrete_lead_controller(),
        reference=0.01,
        horizon_s=10.0,
        sample_time_s=0.025,
        actuator_bounds={"voltage": (-1.0, 1.0)},
        output_bounds={"position": (-0.2, 0.2)},
    )

    assert result.stability.status == "stable"
    assert result.stability.spectral_radius == pytest.approx(0.9369, abs=0.01)
    assert len(result.trace.time_s) == 401

    continuous_plant = plant.model_copy(
        update={"time_domain": "continuous", "sample_time_s": None}
    )
    with pytest.raises(ValueError, match="discrete plant"):
        run_linear_closed_loop(
            continuous_plant,
            discrete_lead_controller(),
            reference=0.01,
            horizon_s=1.0,
            sample_time_s=0.025,
        )
    with pytest.raises(ValueError, match="sample time"):
        run_linear_closed_loop(
            plant,
            discrete_lead_controller(),
            reference=0.01,
            horizon_s=1.0,
            sample_time_s=0.05,
        )


def test_nonlinear_registered_controllers_stay_out_of_linear_runtime():
    plant = TransferFunctionModelSpec(
        numerator=[1.0],
        denominator=[1.0, 1.0],
        input_signal_id="u",
        output_signal_id="y",
    )
    for controller_id in (
        "cartpole_cascaded",
        "vtol_cascaded",
    ):
        with pytest.raises(ValueError, match="registered"):
            run_linear_closed_loop(
                plant,
                RegisteredControllerSpec(controller_id=controller_id),
                reference=0.0,
                horizon_s=1.0,
                sample_time_s=0.01,
            )


def test_fixed_lead_lag_poles_match_independent_polynomial_interconnection():
    plant_denominator = np.array([1.0, 1.0, 0.0])
    controller_denominator = np.polymul([1.0, 8.0], [1.0, 0.05])
    controller_numerator = 0.5 * np.polymul([1.0, 2.0], [1.0, 0.1])
    size = max(
        len(np.polymul(plant_denominator, controller_denominator)),
        len(controller_numerator),
    )
    open_denominator = np.pad(
        np.polymul(plant_denominator, controller_denominator),
        (size - len(np.polymul(plant_denominator, controller_denominator)), 0),
    )
    loop_numerator = np.pad(
        controller_numerator,
        (size - len(controller_numerator), 0),
    )
    expected = sorted(
        np.roots(open_denominator + loop_numerator), key=lambda p: (p.real, p.imag)
    )

    result = run_linear_closed_loop(
        TransferFunctionModelSpec(
            numerator=[1.0],
            denominator=plant_denominator.tolist(),
            input_signal_id="u",
            output_signal_id="y",
        ),
        lead_lag_controller(),
        reference=0.0,
        horizon_s=1.0,
        sample_time_s=0.01,
    )
    actual = sorted(
        [complex(p.real, p.imaginary) for p in result.stability.poles],
        key=lambda p: (p.real, p.imag),
    )
    assert actual == pytest.approx(expected, rel=1e-8, abs=1e-10)


def test_existing_unregistered_linear_controller_behavior_is_unchanged():
    plant = TransferFunctionModelSpec(
        numerator=[1.0],
        denominator=[1.0, 1.0],
        input_signal_id="u",
        output_signal_id="y",
    )
    result = run_linear_closed_loop(
        plant,
        PControllerSpec(kp=0.2),
        reference=1.0,
        horizon_s=2.0,
        sample_time_s=0.01,
    )
    assert result.stability.status == "stable"
