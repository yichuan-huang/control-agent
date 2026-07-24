"""Typed contracts for the interactive closed-loop simulation laboratory.

These contracts intentionally contain no executable expressions or arbitrary
code fields.  A controller can only select one of the registered, audited
runtime architectures represented below.
"""

from __future__ import annotations

import math
from typing import Annotated, Literal, Union

from pydantic import Field, field_validator, model_serializer, model_validator

from cfdc.models.schemas import CFDCModel


class _FrozenFloatDict(dict[str, float]):
    """JSON-compatible scalar map that cannot be mutated after validation."""

    @staticmethod
    def _immutable(*args, **kwargs):
        del args, kwargs
        raise TypeError("registered controller mappings are immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    __ior__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable

    def __deepcopy__(self, memo):
        del memo
        return self


class PControllerSpec(CFDCModel):
    kind: Literal["p"] = "p"
    kp: float


class PIControllerSpec(CFDCModel):
    kind: Literal["pi"] = "pi"
    kp: float
    ki: float
    integrator_limit: float | None = Field(default=None, gt=0.0)


class FilteredPDControllerSpec(CFDCModel):
    kind: Literal["filtered_pd"] = "filtered_pd"
    kp: float
    kd: float
    derivative_source: Literal["measurement"]
    filter_cutoff_rad_s: float = Field(gt=0.0)


class FilteredPIDControllerSpec(CFDCModel):
    kind: Literal["filtered_pid"] = "filtered_pid"
    kp: float
    ki: float
    kd: float
    derivative_source: Literal["measurement"]
    filter_cutoff_rad_s: float = Field(gt=0.0)
    integrator_limit: float | None = Field(default=None, gt=0.0)


class LeadControllerSpec(CFDCModel):
    kind: Literal["lead"] = "lead"
    gain: float
    zero_rad_s: float = Field(gt=0.0)
    pole_rad_s: float = Field(gt=0.0)

    @model_validator(mode="after")
    def validate_lead_architecture(self) -> "LeadControllerSpec":
        if self.pole_rad_s <= self.zero_rad_s:
            raise ValueError(
                "invalid lead architecture: pole_rad_s must exceed zero_rad_s"
            )
        return self


class LagControllerSpec(CFDCModel):
    kind: Literal["lag"] = "lag"
    gain: float
    zero_rad_s: float = Field(gt=0.0)
    pole_rad_s: float = Field(gt=0.0)

    @model_validator(mode="after")
    def validate_lag_architecture(self) -> "LagControllerSpec":
        if self.zero_rad_s <= self.pole_rad_s:
            raise ValueError(
                "invalid lag architecture: zero_rad_s must exceed pole_rad_s"
            )
        return self


class NotchControllerSpec(CFDCModel):
    kind: Literal["notch"] = "notch"
    gain: float
    center_frequency_rad_s: float = Field(gt=0.0)
    zero_damping_ratio: float = Field(gt=0.0)
    pole_damping_ratio: float = Field(gt=0.0)

    @model_validator(mode="after")
    def validate_notch_architecture(self) -> "NotchControllerSpec":
        if self.zero_damping_ratio >= self.pole_damping_ratio:
            raise ValueError(
                "invalid notch architecture: zero_damping_ratio must be "
                "less than pole_damping_ratio"
            )
        return self


class StateFeedbackControllerSpec(CFDCModel):
    kind: Literal["state_feedback"] = "state_feedback"
    gain_matrix: list[list[float]] = Field(min_length=1)
    reference_gain_matrix: list[list[float]] = Field(min_length=1)
    equilibrium_state: list[float] = Field(min_length=1)
    equilibrium_input: list[float] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_complete_dimensions(self) -> "StateFeedbackControllerSpec":
        state_count = len(self.equilibrium_state)
        input_count = len(self.equilibrium_input)
        if len(self.gain_matrix) != input_count or any(
            len(row) != state_count for row in self.gain_matrix
        ):
            raise ValueError(
                "gain_matrix/equilibrium dimensions must be input_count x state_count"
            )
        if len(self.reference_gain_matrix) != input_count:
            raise ValueError(
                "reference_gain_matrix row count must match equilibrium_input"
            )
        reference_count = len(self.reference_gain_matrix[0])
        if reference_count < 1 or any(
            len(row) != reference_count for row in self.reference_gain_matrix
        ):
            raise ValueError("reference_gain_matrix must be a non-empty rectangle")
        return self


class RegisteredControllerSpec(CFDCModel):
    """Reference to an implementation registered by the nonlinear/demo layer."""

    kind: Literal["registered_controller"] = "registered_controller"
    controller_id: Literal[
        "cartpole_cascaded",
        "vtol_cascaded",
        "fixed_lead_lag_cascade",
        "fixed_discrete_lead",
    ]
    parameters: dict[str, float] = Field(default_factory=dict, frozen=True)
    reference: dict[str, float] = Field(default_factory=dict, frozen=True)
    feedforward: dict[str, float] = Field(default_factory=dict, frozen=True)
    configuration: dict[str, float] = Field(default_factory=dict, frozen=True)

    @field_validator(
        "parameters",
        "reference",
        "feedforward",
        "configuration",
    )
    @classmethod
    def freeze_scalar_mapping(cls, values: dict[str, float]) -> dict[str, float]:
        return _FrozenFloatDict(values)

    @model_validator(mode="after")
    def validate_registered_snapshot(self) -> "RegisteredControllerSpec":
        mappings = (
            self.parameters,
            self.reference,
            self.feedforward,
            self.configuration,
        )
        # Preserve the legacy unconfigured reference object used only to prove
        # that the generic linear runtime rejects registered controllers.  A
        # runnable snapshot must be complete.
        if not any(mappings):
            return self
        expected = {
            "cartpole_cascaded": {
                "parameters": {"kp", "kd", "kp_y", "kd_y"},
                "reference": {"position_m"},
                "feedforward_options": (
                    set(),
                    {"position_reference_prefilter"},
                ),
                "configuration": {"theta_reference_limit_rad"},
            },
            "vtol_cascaded": {
                "parameters": {
                    "kp_z",
                    "kd_z",
                    "kp_theta",
                    "kd_theta",
                    "kp_y",
                    "kd_y",
                },
                "reference": {"x_m", "z_m"},
                "feedforward_options": ({"hover_thrust_n"},),
                "configuration": {"tilt_reference_limit_rad"},
            },
            "fixed_lead_lag_cascade": {
                "parameters": {"gain_scale"},
                "reference": set(),
                "feedforward_options": (set(),),
                "configuration": set(),
            },
            "fixed_discrete_lead": {
                "parameters": {"gain_scale"},
                "reference": set(),
                "feedforward_options": (set(),),
                "configuration": set(),
            },
        }.get(self.controller_id)
        if expected is None:
            raise ValueError(
                "configured registered controller is not yet supported by "
                "an exact typed snapshot contract"
            )
        actual = {
            "parameters": set(self.parameters),
            "reference": set(self.reference),
            "configuration": set(self.configuration),
        }
        for field_name in ("parameters", "reference", "configuration"):
            if actual[field_name] != expected[field_name]:
                raise ValueError(
                    f"{self.controller_id} {field_name} must use exact keys; "
                    f"missing={sorted(expected[field_name] - actual[field_name])}, "
                    f"unknown={sorted(actual[field_name] - expected[field_name])}"
                )
        feedforward_keys = set(self.feedforward)
        if feedforward_keys not in expected["feedforward_options"]:
            allowed = [sorted(option) for option in expected["feedforward_options"]]
            raise ValueError(
                f"{self.controller_id} feedforward must match one exact key "
                f"set from {allowed}"
            )
        if any(value <= 0.0 for value in self.configuration.values()):
            raise ValueError(
                "registered controller configuration limits must be positive"
            )
        return self


ControllerRuntimeSpec = Annotated[
    Union[
        PControllerSpec,
        PIControllerSpec,
        FilteredPDControllerSpec,
        FilteredPIDControllerSpec,
        LeadControllerSpec,
        LagControllerSpec,
        NotchControllerSpec,
        StateFeedbackControllerSpec,
        RegisteredControllerSpec,
    ],
    Field(discriminator="kind"),
]


class ComplexValue(CFDCModel):
    real: float
    imaginary: float


class SimulationEvent(CFDCModel):
    kind: Literal[
        "saturation",
        "hard_bound_violation",
        "non_finite",
        "delay_buffer_active",
        "model_validity_boundary_violation",
    ]
    sample_index: int = Field(ge=0)
    time_s: float = Field(ge=0.0)
    message: str = Field(min_length=1)
    channel: str | None = Field(default=None, min_length=1)
    value: float | None = None
    limit: float | None = None
    allowed_range: tuple[float, float] | None = None

    @model_serializer(mode="wrap")
    def serialize_event(self, handler):
        payload = handler(self)
        if self.allowed_range is None:
            payload.pop("allowed_range", None)
        return payload


class SimulationTrace(CFDCModel):
    # A hard arithmetic violation may occur before the first complete sample.
    # In that case an empty trace plus a non_finite event is more truthful than
    # fabricating a numeric sample.
    time_s: list[float] = Field(default_factory=list)
    reference: dict[str, list[float]] = Field(min_length=1)
    states: dict[str, list[float]] = Field(default_factory=dict)
    outputs: dict[str, list[float]] = Field(min_length=1)
    requested_controls: dict[str, list[float]] = Field(min_length=1)
    applied_controls: dict[str, list[float]] = Field(min_length=1)
    events: list[SimulationEvent] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_channel_lengths_and_time(self) -> "SimulationTrace":
        sample_count = len(self.time_s)
        if sample_count > 20_000:
            # Pydantic's max_length error is technically enough, but this
            # explicit wording is stable for API clients and audit logs.
            raise ValueError("SimulationTrace cannot exceed 20,000 samples")
        if any(
            later <= earlier for earlier, later in zip(self.time_s, self.time_s[1:])
        ):
            raise ValueError("time_s must be strictly increasing")
        channel_groups = {
            "reference": self.reference,
            "states": self.states,
            "outputs": self.outputs,
            "requested_controls": self.requested_controls,
            "applied_controls": self.applied_controls,
        }
        mismatches = [
            f"{group}.{name}"
            for group, channels in channel_groups.items()
            for name, values in channels.items()
            if len(values) != sample_count
        ]
        if mismatches:
            raise ValueError(
                "all channel lengths must match time_s; mismatches="
                + ", ".join(mismatches)
            )
        return self


class NonlinearScenarioEvidence(CFDCModel):
    """Auditable outcome of one registered deterministic perturbation."""

    scenario_id: str = Field(min_length=1)
    passed: bool
    trajectory_finite: bool
    trajectory_bounded: bool
    tail_error_envelope_contraction: float
    saturation_fraction: float = Field(ge=0.0, le=1.0)
    hard_failure: bool = False
    sample_count: int = Field(ge=0, le=20_000)
    violations: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_passed_scenario(self) -> "NonlinearScenarioEvidence":
        if self.hard_failure and self.passed:
            raise ValueError("a hard-failed nonlinear scenario cannot pass")
        if self.passed and (
            not self.trajectory_finite
            or not self.trajectory_bounded
            or self.tail_error_envelope_contraction < 0.10 - 1e-12
            or self.saturation_fraction > 0.10
            or self.violations
        ):
            raise ValueError(
                "a passed nonlinear scenario requires finite bounded data, "
                "at least 10% tail contraction, no sustained saturation, "
                "and no violations"
            )
        return self


class StabilityDecision(CFDCModel):
    status: Literal["stable", "unstable", "inconclusive"]
    analysis_domain: Literal["continuous", "discrete"]
    pole_analysis_method: Literal[
        "exact_continuous_interconnection",
        "third_order_pade_auxiliary",
        "exact_discrete_interconnection",
        "exact_discrete_delay_augmentation",
        "registered_nonlinear_local_linearization",
    ]
    registered_template_id: (
        Literal[
            "underactuated_cartpole",
            "vtol_cascaded",
        ]
        | None
    ) = None
    poles: list[ComplexValue] = Field(default_factory=list)
    spectral_radius: float | None = Field(default=None, ge=0.0)
    trajectory_finite: bool
    trajectory_bounded: bool
    tail_error_envelope_contraction: float
    saturation_fraction: float = Field(ge=0.0, le=1.0)
    hard_failure: bool = False
    violations: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(min_length=1)
    scenario_evidence: list[NonlinearScenarioEvidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_domain_evidence(self) -> "StabilityDecision":
        if self.analysis_domain == "continuous" and self.spectral_radius is not None:
            raise ValueError("spectral_radius is only defined for discrete analysis")
        if self.analysis_domain == "discrete" and self.spectral_radius is None:
            raise ValueError("discrete analysis requires spectral_radius")
        continuous_methods = {
            "exact_continuous_interconnection",
            "third_order_pade_auxiliary",
            "registered_nonlinear_local_linearization",
        }
        discrete_methods = {
            "exact_discrete_interconnection",
            "exact_discrete_delay_augmentation",
        }
        expected_methods = (
            continuous_methods
            if self.analysis_domain == "continuous"
            else discrete_methods
        )
        if self.pole_analysis_method not in expected_methods:
            raise ValueError(
                "pole_analysis_method must match the declared analysis domain"
            )
        registered_scenarios = {
            "underactuated_cartpole": {
                "angle_positive",
                "angle_negative",
                "position_and_angle_positive",
                "position_and_angle_negative",
                "mixed_velocity",
            },
            "vtol_cascaded": {
                "lateral_position",
                "altitude",
                "pitch",
                "combined_positive",
                "combined_negative",
            },
        }
        is_registered = (
            self.pole_analysis_method == "registered_nonlinear_local_linearization"
        )
        if not is_registered and self.registered_template_id is not None:
            raise ValueError(
                "registered_template_id is only valid for registered nonlinear analysis"
            )
        if is_registered:
            if self.registered_template_id is None:
                raise ValueError("registered nonlinear analysis requires a template ID")
            expected_scenarios = registered_scenarios[self.registered_template_id]
            scenario_ids = [item.scenario_id for item in self.scenario_evidence]
            if (
                len(scenario_ids) != len(set(scenario_ids))
                or set(scenario_ids) != expected_scenarios
            ):
                raise ValueError(
                    "registered nonlinear analysis requires the exact unique "
                    "deterministic scenario IDs"
                )
            expected_pole_count = (
                4 if self.registered_template_id == "underactuated_cartpole" else 6
            )
            if len(self.poles) != expected_pole_count:
                raise ValueError(
                    "registered nonlinear analysis must report every local "
                    "closed-loop eigenvalue"
                )
        if (
            self.analysis_domain == "discrete"
            and self.poles
            and self.spectral_radius is not None
        ):
            pole_radius = max(
                math.hypot(pole.real, pole.imaginary) for pole in self.poles
            )
            if not math.isclose(
                self.spectral_radius,
                pole_radius,
                rel_tol=1e-9,
                abs_tol=1e-12,
            ):
                raise ValueError(
                    "spectral_radius must match the maximum recorded pole magnitude"
                )
        if self.status == "stable":
            if (
                not self.trajectory_finite
                or not self.trajectory_bounded
                or self.saturation_fraction > 0.10
                or self.hard_failure
                or self.violations
            ):
                raise ValueError(
                    "a stable decision requires a finite bounded trajectory, "
                    "saturation_fraction <= 0.1, and no violations"
                )
            if self.analysis_domain == "continuous" and any(
                pole.real >= -1e-6 for pole in self.poles
            ):
                raise ValueError(
                    "a continuous stable decision requires every recorded "
                    "pole real part to be below -1e-6"
                )
            if (
                self.analysis_domain == "discrete"
                and self.spectral_radius is not None
                and self.spectral_radius >= 1.0 - 1e-6
            ):
                raise ValueError(
                    "a discrete stable decision requires spectral_radius below 1-1e-6"
                )
            if self.scenario_evidence and (
                len(self.scenario_evidence) != 5
                or any(not item.passed for item in self.scenario_evidence)
            ):
                raise ValueError(
                    "a stable registered nonlinear decision requires exactly "
                    "five passed deterministic scenarios"
                )
        return self


__all__ = [
    "ComplexValue",
    "ControllerRuntimeSpec",
    "FilteredPDControllerSpec",
    "FilteredPIDControllerSpec",
    "LagControllerSpec",
    "LeadControllerSpec",
    "NotchControllerSpec",
    "NonlinearScenarioEvidence",
    "PControllerSpec",
    "PIControllerSpec",
    "RegisteredControllerSpec",
    "SimulationEvent",
    "SimulationTrace",
    "StateFeedbackControllerSpec",
    "StabilityDecision",
]
