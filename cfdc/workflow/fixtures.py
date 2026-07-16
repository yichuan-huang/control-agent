from __future__ import annotations

from cfdc.models import DemoPlantFixture, DemoPlantFixtureCatalog


def default_demo_plant_fixture_catalog() -> DemoPlantFixtureCatalog:
    """Return preregistered demo plants; never use these as user-object evidence."""

    return DemoPlantFixtureCatalog(
        fixtures=[
            DemoPlantFixture(
                fixture_id="demo_first_order_lag",
                method_profile_id="first_order_lag",
                simulator_backend="scalar_first_order",
                nominal_parameters={"static_gain": 2.0, "time_constant": 5.0},
                change_scenario_id="gain_and_time_constant_drift",
            ),
            DemoPlantFixture(
                fixture_id="demo_first_order_lag_with_delay",
                method_profile_id="first_order_lag_with_delay",
                simulator_backend="scalar_first_order_delay",
                nominal_parameters={
                    "static_gain": 1.5,
                    "time_constant": 8.0,
                    "dead_time": 2.0,
                },
                change_scenario_id="gain_and_time_constant_drift",
            ),
            DemoPlantFixture(
                fixture_id="demo_second_order_oscillator",
                method_profile_id="second_order_oscillator",
                simulator_backend="scalar_second_order",
                nominal_parameters={
                    "natural_frequency": 3.0,
                    "damping_ratio": 0.18,
                    "input_gain": 1.0,
                },
                change_scenario_id="frequency_and_gain_drift",
            ),
            DemoPlantFixture(
                fixture_id="demo_double_integrator",
                method_profile_id="double_integrator",
                simulator_backend="scalar_double_integrator",
                nominal_parameters={"input_gain": 0.8},
                change_scenario_id="input_gain_drift",
            ),
            DemoPlantFixture(
                fixture_id="demo_nmp_inverse_response",
                method_profile_id="nmp_inverse_response",
                simulator_backend="scalar_inverse_response",
                nominal_parameters={
                    "static_gain": 1.0,
                    "time_constant": 6.0,
                    "inverse_response_severity": 0.25,
                },
                change_scenario_id="gain_and_inverse_response_drift",
            ),
            DemoPlantFixture(
                fixture_id="demo_generic_unstable_higher_order",
                method_profile_id="generic_unstable_higher_order",
                simulator_backend="generic_unstable",
                nominal_parameters={"natural_frequency": 2.4, "input_gain": 0.7},
                change_scenario_id="unstable_mode_drift",
            ),
            DemoPlantFixture(
                fixture_id="demo_underactuated_cartpole",
                method_profile_id="underactuated_cartpole",
                simulator_backend="cartpole",
                nominal_parameters={
                    "cart_mass_kg": 0.5,
                    "pole_mass_kg": 0.2,
                    "com_length_m": 0.3,
                    "pole_inertia_kg_m2": 0.006,
                    "cart_friction_n_s_m": 0.1,
                    "gravity_m_s2": 9.8,
                    "force_limit_n": 10.0,
                    "cart_position_limit_m": 2.4,
                },
                change_scenario_id="pole_frequency_drift",
            ),
            DemoPlantFixture(
                fixture_id="demo_vtol_cascaded",
                method_profile_id="vtol_cascaded",
                simulator_backend="vtol",
                nominal_parameters={
                    "mass_kg": 1.2,
                    "pitch_inertia_kg_m2": 0.035,
                    "gravity_m_s2": 9.81,
                    "linear_drag_n_s_m": 0.08,
                    "pitch_damping_n_m_s": 0.015,
                    "thrust_min_n": 0.0,
                    "thrust_max_n": 18.0,
                    "torque_limit_n_m": 0.9,
                },
                change_scenario_id="payload_and_inertia_drift",
            ),
            DemoPlantFixture(
                fixture_id="demo_mimo_2x2_coupled",
                method_profile_id="mimo_2x2_coupled",
                simulator_backend="mimo_2x2",
                nominal_parameters={
                    "local_gain_matrix": [[2.0, 0.7], [0.5, 1.6]],
                    "local_time_constant": 1.0,
                },
                change_scenario_id="coupling_matrix_drift",
            ),
        ]
    )


def demo_fixture_by_method_profile_id(method_profile_id: str) -> DemoPlantFixture:
    for fixture in default_demo_plant_fixture_catalog().fixtures:
        if fixture.method_profile_id == method_profile_id:
            return fixture
    raise ValueError(f"no demo fixture is registered for method profile '{method_profile_id}'")
