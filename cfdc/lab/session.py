"""Recoverable state machine for the CFDC stability-only simulation loop.

The kernel is deliberately independent from Gradio and from the five-stage
diagnostic orchestrator.  Every public action is copy-on-write, revisioned,
and validated through the typed contracts in this module.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import re
from typing import Any, Literal, Protocol
from uuid import uuid4

import numpy as np
from pydantic import Field, TypeAdapter, model_validator

from cfdc.lab.contracts import (
    ComplexValue,
    ControllerRuntimeSpec,
    NonlinearScenarioEvidence,
    RegisteredControllerSpec,
    SimulationTrace,
    StabilityDecision,
)
from cfdc.lab.model_validity import SimulationResultGuard
from cfdc.models.schemas import (
    CFDCModel,
    ExecutableModelSpec,
    RegisteredNonlinearModelSpec,
)


SessionState = Literal[
    "model_review",
    "controller_ready",
    "trial_pending",
    "evaluating",
    "stable",
    "needs_adjustment",
    "rolled_back",
    "frozen",
    "inconclusive",
    "budget_exhausted",
    "cancelled",
]
TERMINAL_STATES = frozenset(
    {"stable", "frozen", "inconclusive", "budget_exhausted", "cancelled"}
)
_SENSITIVE_KEYS = frozenset({"apikey", "authorization", "token", "secret", "password"})
_CONTROLLER_ADAPTER = TypeAdapter(ControllerRuntimeSpec)
_MAX_IMPORT_BYTES = 5 * 1024 * 1024
_MAX_JSON_DEPTH = 64


class SessionActionError(ValueError):
    """An action is not legal for the current state or data."""


class StaleRevisionError(SessionActionError):
    """The caller acted on an obsolete session snapshot."""


class ProposalValidationError(SessionActionError):
    """A gain proposal crossed a structural or safety boundary."""


class SessionImportError(ValueError):
    """A serialized session failed closed validation."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_for_hash(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_for_hash(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_for_hash(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite values cannot be hashed")
        return 0.0 if value == 0.0 else value
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _normalize_for_hash(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _without(payload: Mapping[str, Any], *keys: str) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key not in keys}


def _scan_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"non-finite value at {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _scan_finite(item, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _scan_finite(item, f"{path}[{index}]")


def _normalized_sensitive_key(key: str) -> str:
    return re.sub(r"[_\-\s]", "", key).casefold()


def _scan_sensitive_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = _normalized_sensitive_key(str(key))
            if any(marker in normalized for marker in _SENSITIVE_KEYS):
                raise ValueError(f"sensitive key rejected at {path}.{key}")
            _scan_sensitive_keys(item, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _scan_sensitive_keys(item, f"{path}[{index}]")


def _json_depth(value: Any, depth: int = 0) -> int:
    if depth > _MAX_JSON_DEPTH:
        return depth
    if isinstance(value, Mapping):
        return max([depth] + [_json_depth(item, depth + 1) for item in value.values()])
    if isinstance(value, list):
        return max([depth] + [_json_depth(item, depth + 1) for item in value])
    return depth


class TuningParameterRule(CFDCModel):
    name: str = Field(min_length=1, pattern=r"^[A-Za-z][A-Za-z0-9_]*$")
    binding: str = Field(min_length=1)
    lower_bound: float
    upper_bound: float
    stabilizing_direction: Literal[-1, 1] = 1
    zero_step_scale: float | None = Field(default=None, gt=0.0)

    @model_validator(mode="after")
    def validate_bounds(self) -> "TuningParameterRule":
        if self.lower_bound >= self.upper_bound:
            raise ValueError("tuning lower_bound must be below upper_bound")
        return self


class TuningProfile(CFDCModel):
    profile_id: str = Field(min_length=1)
    open_loop_behavior: Literal["stable", "unstable"]
    step_fraction: float = Field(ge=0.05, le=0.10)
    parameters: list[TuningParameterRule] = Field(min_length=1)
    max_trials: Literal[20] = 20

    @model_validator(mode="after")
    def validate_parameter_identity(self) -> "TuningProfile":
        names = [item.name for item in self.parameters]
        if len(names) != len(set(names)):
            raise ValueError("tuning parameter names must be unique")
        bindings = [item.binding for item in self.parameters]
        if len(bindings) != len(set(bindings)):
            raise ValueError("tuning parameter bindings must be unique")
        return self

    @property
    def whitelist(self) -> list[str]:
        return [item.name for item in self.parameters]


class ParameterProposal(CFDCModel):
    schema_version: Literal["parameter_proposal/v1"] = "parameter_proposal/v1"
    proposal_id: str = Field(pattern=r"^proposal-[0-9a-f]{20}$")
    source: Literal["deterministic", "llm"]
    session_id: str = Field(min_length=1)
    base_revision: int = Field(ge=0)
    base_trial_iteration: int = Field(ge=0, le=20)
    architecture_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    whitelist: list[str] = Field(min_length=1)
    old_parameters: dict[str, float] = Field(min_length=1)
    new_parameters: dict[str, float] = Field(min_length=1)
    relative_change: dict[str, float] = Field(min_length=1)
    rationale: str = Field(min_length=1, max_length=4000)
    checksum: str = Field(pattern=r"^[0-9a-f]{64}$")
    approval_state: Literal["not_required", "pending", "approved", "rejected", "stale"]

    @model_validator(mode="after")
    def validate_keysets(self) -> "ParameterProposal":
        expected = set(self.whitelist)
        if len(self.whitelist) != len(expected):
            raise ValueError("proposal whitelist must be unique")
        for name, values in (
            ("old_parameters", self.old_parameters),
            ("new_parameters", self.new_parameters),
            ("relative_change", self.relative_change),
        ):
            if set(values) != expected:
                raise ValueError(f"{name} must match the exact whitelist")
        if self.source == "llm" and self.approval_state == "not_required":
            raise ValueError("LLM proposals always require explicit approval")
        if self.source == "deterministic" and self.approval_state == "pending":
            raise ValueError("deterministic proposals do not await approval")
        return self


class TransitionRecord(CFDCModel):
    action: str = Field(min_length=1)
    from_state: SessionState
    to_state: SessionState
    revision_before: int = Field(ge=0)
    revision_after: int = Field(ge=1)
    occurred_at: str = Field(min_length=1)
    reason: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_revision_step(self) -> "TransitionRecord":
        if self.revision_after != self.revision_before + 1:
            raise ValueError("each transition must increment revision exactly once")
        return self


class LLMMessageRecord(CFDCModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(max_length=50_000)


class LLMCallRecord(CFDCModel):
    schema_version: Literal["llm_call_record/v1"] = "llm_call_record/v1"
    call_id: str = Field(pattern=r"^llm-[0-9a-f]{20}$")
    operation: Literal["model_proposal", "gain_proposal"]
    provider: str = Field(min_length=1, max_length=200)
    model: str = Field(min_length=1, max_length=300)
    messages: list[LLMMessageRecord] = Field(max_length=20)
    structured_response: dict[str, Any] | None = None
    invalid_raw_text: str | None = Field(default=None, max_length=20_000)
    validation_status: Literal["accepted", "rejected", "need_more", "error"]
    validation_errors: list[str] = Field(default_factory=list, max_length=40)
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    occurred_at: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_sanitized_payload(self) -> "LLMCallRecord":
        payload = self.model_dump(
            mode="json",
            exclude={"request_sha256", "response_sha256"},
        )
        _scan_finite(payload)
        _scan_sensitive_keys(payload)
        expected_request = _sha256(
            [message.model_dump(mode="json") for message in self.messages]
        )
        response = (
            self.structured_response
            if self.structured_response is not None
            else {"invalid_raw_text": self.invalid_raw_text or ""}
        )
        if self.request_sha256 != expected_request:
            raise ValueError("LLM request hash mismatch")
        if self.response_sha256 != _sha256(response):
            raise ValueError("LLM response hash mismatch")
        identity_seed = {
            "operation": self.operation,
            "provider": self.provider,
            "model": self.model,
            "messages": [message.model_dump(mode="json") for message in self.messages],
            "response": response,
            "occurred_at": self.occurred_at,
        }
        if self.call_id != f"llm-{_sha256(identity_seed)[:20]}":
            raise ValueError("LLM call ID/hash mismatch")
        return self


class TrialRecord(CFDCModel):
    schema_version: Literal["trial_record/v1"] = "trial_record/v1"
    iteration: int = Field(ge=1, le=20)
    controller: ControllerRuntimeSpec
    proposal: ParameterProposal | None = None
    traces: list[SimulationTrace] = Field(min_length=1, max_length=5)
    original_sample_counts: list[int] = Field(min_length=1, max_length=5)
    trace_storage_policy: Literal["full", "deterministic_decimation_64"] = "full"
    stability: StabilityDecision
    creation_source: Literal["initial", "deterministic", "llm", "manual_restore"]
    hard_violation: bool = False
    rolled_back: bool = False
    rollback_reason: str | None = Field(default=None, max_length=2000)
    stability_score: float
    trial_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    occurred_at: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_trial_integrity(self) -> "TrialRecord":
        if len(self.original_sample_counts) != len(self.traces):
            raise ValueError("original_sample_counts must align with stored traces")
        if any(
            original < len(trace.time_s)
            for original, trace in zip(self.original_sample_counts, self.traces)
        ):
            raise ValueError("stored trace cannot exceed its original sample count")
        expected_policy = (
            "deterministic_decimation_64"
            if any(
                original > len(trace.time_s)
                for original, trace in zip(self.original_sample_counts, self.traces)
            )
            else "full"
        )
        if self.trace_storage_policy != expected_policy:
            raise ValueError("trace storage policy/count evidence mismatch")
        if self.rolled_back and not self.hard_violation:
            raise ValueError("automatic rollback requires a hard violation")
        if self.hard_violation and not self.rollback_reason:
            raise ValueError("hard violations require a rollback reason")
        payload = self.model_dump(mode="json", exclude={"trial_hash"})
        if self.trial_hash != _sha256(payload):
            raise ValueError("trial hash mismatch")
        return self


class SimulationRunConfig(CFDCModel):
    reference: dict[str, float] = Field(min_length=1)
    horizon_s: float = Field(gt=0.0)
    sample_time_s: float = Field(gt=0.0)
    actuator_bounds: dict[str, tuple[float, float]] = Field(min_length=1)
    state_bounds: dict[str, tuple[float, float]] = Field(default_factory=dict)
    output_bounds: dict[str, tuple[float, float]] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_budget_and_bounds(self) -> "SimulationRunConfig":
        sample_count = math.floor(self.horizon_s / self.sample_time_s + 1e-12) + 1
        if sample_count > 20_000:
            raise ValueError("simulation configuration exceeds 20,000 samples")
        for group in (
            self.actuator_bounds,
            self.state_bounds,
            self.output_bounds,
        ):
            if any(lower >= upper for lower, upper in group.values()):
                raise ValueError("every runtime lower bound must be below upper")
        return self


class SimulationSession(CFDCModel):
    schema_version: Literal["simulation_session/v1"] = "simulation_session/v1"
    session_id: str = Field(pattern=r"^session-[0-9a-f]{20}$")
    revision: int = Field(ge=0)
    origin: Literal[
        "llm_proposed_model_hypothesis",
        "stage5_candidate_model",
        "stage5_candidate_llm_model",
    ]
    evidence_boundary: Literal[
        "llm_proposed_model_hypothesis",
        "stage5_candidate_model",
    ]
    source_run_id: str | None = Field(default=None, min_length=1, max_length=200)
    source_plant_id: str | None = Field(default=None, min_length=1, max_length=200)
    source_controller_architecture: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    source_link_sha256: str | None = Field(
        default=None,
        pattern=r"^[0-9a-f]{64}$",
    )
    source_candidate_plant_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    pending_model: ExecutableModelSpec | None = None
    confirmed_model: ExecutableModelSpec | None = None
    model_assumptions: list[str] = Field(default_factory=list, max_length=20)
    model_confirmed: bool = False
    run_config: SimulationRunConfig | None = None
    initial_controller: ControllerRuntimeSpec | None = None
    current_safe_controller: ControllerRuntimeSpec | None = None
    trial_controller: ControllerRuntimeSpec | None = None
    pending_proposal: ParameterProposal | None = None
    trials: list[TrialRecord] = Field(default_factory=list, max_length=20)
    llm_calls: list[LLMCallRecord] = Field(default_factory=list, max_length=100)
    tuning_profile: TuningProfile | None = None
    soft_worsening_count: int = Field(default=0, ge=0, le=2)
    state: SessionState = "model_review"
    termination_reason: str | None = Field(default=None, max_length=2000)
    transition_history: list[TransitionRecord] = Field(
        default_factory=list, max_length=1000
    )
    content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_session_integrity(self) -> "SimulationSession":
        expected_boundary = (
            "llm_proposed_model_hypothesis"
            if self.origin == "stage5_candidate_llm_model"
            else self.origin
        )
        if self.evidence_boundary != expected_boundary:
            raise ValueError("origin and evidence boundary are inconsistent")
        stage5_metadata = (
            self.source_run_id,
            self.source_plant_id,
            self.source_controller_architecture,
            self.source_link_sha256,
        )
        if self.origin in {
            "stage5_candidate_model",
            "stage5_candidate_llm_model",
        }:
            if any(value is None for value in stage5_metadata):
                raise ValueError("stage5 sessions require complete source metadata")
        elif any(value is not None for value in stage5_metadata):
            raise ValueError("only stage5 sessions carry source metadata")
        if self.model_confirmed != (self.confirmed_model is not None):
            raise ValueError("model confirmation flag/model are inconsistent")
        if self.model_confirmed and self.pending_model != self.confirmed_model:
            raise ValueError("confirmed model must equal the reviewed model")
        if (
            self.state
            not in {
                "model_review",
                "cancelled",
                "inconclusive",
            }
            and not self.model_confirmed
        ):
            raise ValueError("no state may pass model review without confirmation")
        if self.state in {
            "trial_pending",
            "evaluating",
            "stable",
            "needs_adjustment",
            "rolled_back",
            "frozen",
            "budget_exhausted",
        } and (
            self.trial_controller is None
            or self.initial_controller is None
            or self.current_safe_controller is None
            or self.tuning_profile is None
        ):
            raise ValueError("controller-loop states require complete snapshots")
        if self.trials and [trial.iteration for trial in self.trials] != list(
            range(1, len(self.trials) + 1)
        ):
            raise ValueError("trial iterations must be contiguous and monotonic")
        if len(self.trials) == 20 and self.state not in TERMINAL_STATES:
            raise ValueError("a 20-trial session must be in a terminal state")
        if self.transition_history:
            last = self.transition_history[-1]
            if last.revision_after != self.revision or last.to_state != self.state:
                raise ValueError(
                    "transition history must end at session revision/state"
                )
            if any(
                later.revision_before != earlier.revision_after
                or later.from_state != earlier.to_state
                for earlier, later in zip(
                    self.transition_history, self.transition_history[1:]
                )
            ):
                raise ValueError("transition history must form one exact chain")
        elif self.revision != 0:
            raise ValueError("nonzero revision requires transition history")
        if self.pending_proposal is not None:
            _validate_proposal_checksum(self.pending_proposal)
            if self.pending_proposal.session_id != self.session_id:
                raise ValueError("proposal belongs to another session")
        payload = self.model_dump(mode="json", exclude={"content_sha256"})
        expected = _sha256(payload)
        if self.content_sha256 is None:
            self.content_sha256 = expected
        elif self.content_sha256 != expected:
            raise ValueError("session content checksum mismatch")
        return self


class SimulationRunner(Protocol):
    def __call__(
        self,
        model: ExecutableModelSpec,
        controller: ControllerRuntimeSpec,
    ) -> Any: ...


_REGISTERED_PARAMETER_KEYS: dict[str, tuple[str, ...]] = {
    "cartpole_cascaded": ("kp", "kd", "kp_y", "kd_y"),
    "vtol_cascaded": (
        "kp_z",
        "kd_z",
        "kp_theta",
        "kd_theta",
        "kp_y",
        "kd_y",
    ),
    "fixed_lead_lag_cascade": ("gain_scale",),
    "fixed_discrete_lead": ("gain_scale",),
}


def _binding_parts(binding: str) -> tuple[str, ...]:
    parts = tuple(binding.split("."))
    if not parts or any(not part for part in parts):
        raise ProposalValidationError("invalid empty controller binding")
    return parts


def _allowed_bindings(controller: ControllerRuntimeSpec) -> set[str]:
    kind = controller.kind
    if kind == "p":
        return {"kp"}
    if kind == "pi":
        return {"kp", "ki"}
    if kind == "filtered_pd":
        return {"kp", "kd"}
    if kind == "filtered_pid":
        return {"kp", "ki", "kd"}
    if kind in {"lead", "lag", "notch"}:
        return {"gain"}
    if kind == "state_feedback":
        return {
            f"gain_matrix.{row}.{column}"
            for row, values in enumerate(controller.gain_matrix)
            for column in range(len(values))
        }
    if kind == "registered_controller":
        keys = _REGISTERED_PARAMETER_KEYS.get(controller.controller_id)
        if keys is None or set(controller.parameters) != set(keys):
            raise ProposalValidationError(
                "registered controller does not match an exact gain registry"
            )
        return {f"parameters.{key}" for key in keys}
    raise ProposalValidationError(f"unsupported controller kind: {kind}")


def _read_binding(controller: ControllerRuntimeSpec, binding: str) -> float:
    if binding not in _allowed_bindings(controller):
        raise ProposalValidationError(
            f"binding is not tunable for this architecture: {binding}"
        )
    value: Any = controller.model_dump(mode="python")
    for part in _binding_parts(binding):
        if isinstance(value, list):
            try:
                value = value[int(part)]
            except (ValueError, IndexError) as exc:
                raise ProposalValidationError(
                    f"invalid indexed controller binding: {binding}"
                ) from exc
        elif isinstance(value, Mapping) and part in value:
            value = value[part]
        else:
            raise ProposalValidationError(
                f"controller binding does not exist: {binding}"
            )
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProposalValidationError(
            f"controller binding is not a numeric gain: {binding}"
        )
    return float(value)


def extract_tunable_parameters(
    controller: ControllerRuntimeSpec,
    profile: TuningProfile,
) -> dict[str, float]:
    """Extract only explicitly registered/declared gains."""

    return {
        rule.name: _read_binding(controller, rule.binding)
        for rule in profile.parameters
    }


def _write_binding(payload: dict[str, Any], binding: str, value: float) -> None:
    target: Any = payload
    parts = _binding_parts(binding)
    for part in parts[:-1]:
        if isinstance(target, list):
            target = target[int(part)]
        else:
            target = target[part]
    final = parts[-1]
    if isinstance(target, list):
        target[int(final)] = value
    else:
        target[final] = value


def rebuild_controller(
    controller: ControllerRuntimeSpec,
    profile: TuningProfile,
    parameters: Mapping[str, float],
) -> ControllerRuntimeSpec:
    """Rebuild a controller without permitting structural dictionary patches."""

    if set(parameters) != set(profile.whitelist):
        raise ProposalValidationError(
            "new parameter map must match the exact tuning whitelist"
        )
    payload = controller.model_dump(mode="python")
    allowed = _allowed_bindings(controller)
    for rule in profile.parameters:
        if rule.binding not in allowed:
            raise ProposalValidationError(
                f"profile binding is not allowed: {rule.binding}"
            )
        value = parameters[rule.name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ProposalValidationError(f"gain {rule.name} must be a finite number")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ProposalValidationError(f"gain {rule.name} must be finite")
        if numeric < rule.lower_bound or numeric > rule.upper_bound:
            raise ProposalValidationError(
                f"gain {rule.name} is outside its declared bounds"
            )
        _write_binding(payload, rule.binding, numeric)
    rebuilt = _CONTROLLER_ADAPTER.validate_python(payload)
    if _architecture_hash(rebuilt, profile) != _architecture_hash(controller, profile):
        raise ProposalValidationError("controller architecture changed")
    return rebuilt


def _architecture_hash(
    controller: ControllerRuntimeSpec, profile: TuningProfile
) -> str:
    payload = controller.model_dump(mode="python")
    allowed = _allowed_bindings(controller)
    for rule in profile.parameters:
        if rule.binding not in allowed:
            raise ProposalValidationError(
                f"profile binding is not allowed: {rule.binding}"
            )
        _write_binding(payload, rule.binding, "<tunable>")
    return _sha256(payload)


def controller_architecture_hash(
    controller: ControllerRuntimeSpec, profile: TuningProfile
) -> str:
    """Return the hash of kind, dimensions, and immutable configuration."""

    return _architecture_hash(controller, profile)


def _relative_change(old: float, new: float, rule: TuningParameterRule) -> float:
    if old != 0.0:
        return abs(new - old) / abs(old)
    if new == 0.0:
        return 0.0
    if rule.zero_step_scale is None:
        raise ProposalValidationError(
            f"zero gain {rule.name} cannot move without zero_step_scale"
        )
    return abs(new) / rule.zero_step_scale


def _proposal_checksum_payload(
    *,
    source: str,
    session_id: str,
    base_revision: int,
    base_trial_iteration: int,
    architecture_sha256: str,
    whitelist: Sequence[str],
    old_parameters: Mapping[str, float],
    new_parameters: Mapping[str, float],
    relative_change: Mapping[str, float],
    rationale: str,
) -> dict[str, Any]:
    return {
        "source": source,
        "session_id": session_id,
        "base_revision": base_revision,
        "base_trial_iteration": base_trial_iteration,
        "architecture_sha256": architecture_sha256,
        "whitelist": list(whitelist),
        "old_parameters": dict(old_parameters),
        "new_parameters": dict(new_parameters),
        "relative_change": dict(relative_change),
        "rationale": rationale,
    }


def _validate_proposal_checksum(proposal: ParameterProposal) -> None:
    payload = _proposal_checksum_payload(
        source=proposal.source,
        session_id=proposal.session_id,
        base_revision=proposal.base_revision,
        base_trial_iteration=proposal.base_trial_iteration,
        architecture_sha256=proposal.architecture_sha256,
        whitelist=proposal.whitelist,
        old_parameters=proposal.old_parameters,
        new_parameters=proposal.new_parameters,
        relative_change=proposal.relative_change,
        rationale=proposal.rationale,
    )
    checksum = _sha256(payload)
    if proposal.checksum != checksum:
        raise ValueError("proposal checksum mismatch")
    if proposal.proposal_id != f"proposal-{checksum[:20]}":
        raise ValueError("proposal ID/checksum mismatch")


def build_parameter_proposal(
    session: SimulationSession,
    *,
    source: Literal["deterministic", "llm"],
    new_parameters: Mapping[str, float],
    rationale: str,
) -> ParameterProposal:
    """Build a backend-owned proposal after enforcing every gain boundary."""

    if session.trial_controller is None or session.tuning_profile is None:
        raise ProposalValidationError("session has no tunable controller")
    profile = session.tuning_profile
    old = extract_tunable_parameters(session.trial_controller, profile)
    if set(new_parameters) != set(old):
        missing = sorted(set(old) - set(new_parameters))
        unknown = sorted(set(new_parameters) - set(old))
        raise ProposalValidationError(
            f"proposal must use exact whitelist; missing={missing}, unknown={unknown}"
        )
    new: dict[str, float] = {}
    changes: dict[str, float] = {}
    rules = {rule.name: rule for rule in profile.parameters}
    for name in profile.whitelist:
        raw = new_parameters[name]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ProposalValidationError(f"gain {name} must be numeric")
        value = 0.0 if float(raw) == 0.0 else float(raw)
        if not math.isfinite(value):
            raise ProposalValidationError(f"gain {name} must be finite")
        rule = rules[name]
        if not rule.lower_bound <= value <= rule.upper_bound:
            raise ProposalValidationError(f"gain {name} is outside its declared bounds")
        relative = _relative_change(old[name], value, rule)
        if relative > 0.10 + 1e-12:
            raise ProposalValidationError(f"gain {name} changes by more than 10%")
        new[name] = value
        changes[name] = relative
    if not any(change > 1e-12 for change in changes.values()):
        raise ProposalValidationError(
            "proposal must change at least one whitelisted gain"
        )
    # Rebuilding here proves the complete typed architecture remains valid.
    rebuilt = rebuild_controller(session.trial_controller, profile, new)
    architecture_sha256 = _architecture_hash(rebuilt, profile)
    payload = _proposal_checksum_payload(
        source=source,
        session_id=session.session_id,
        base_revision=session.revision,
        base_trial_iteration=len(session.trials),
        architecture_sha256=architecture_sha256,
        whitelist=profile.whitelist,
        old_parameters=old,
        new_parameters=new,
        relative_change=changes,
        rationale=rationale,
    )
    checksum = _sha256(payload)
    return ParameterProposal(
        proposal_id=f"proposal-{checksum[:20]}",
        source=source,
        session_id=session.session_id,
        base_revision=session.revision,
        base_trial_iteration=len(session.trials),
        architecture_sha256=architecture_sha256,
        whitelist=profile.whitelist,
        old_parameters=old,
        new_parameters=new,
        relative_change=changes,
        rationale=rationale,
        checksum=checksum,
        approval_state="pending" if source == "llm" else "not_required",
    )


def _rehash_session(payload: Mapping[str, Any]) -> SimulationSession:
    data = deepcopy(dict(payload))
    data["content_sha256"] = None
    return SimulationSession.model_validate(data)


def _copy_session(session: SimulationSession) -> SimulationSession:
    return SimulationSession.model_validate(session.model_dump(mode="python"))


def _expect_revision(session: SimulationSession, expected_revision: int | None) -> int:
    expected = session.revision if expected_revision is None else expected_revision
    if expected != session.revision:
        raise StaleRevisionError(
            f"stale session revision {expected}; current={session.revision}"
        )
    return expected


def _transition(
    session: SimulationSession,
    *,
    to_state: SessionState,
    action: str,
    reason: str | None = None,
    updates: Mapping[str, Any] | None = None,
) -> SimulationSession:
    payload = session.model_dump(mode="python")
    before = session.revision
    payload.update(deepcopy(dict(updates or {})))
    payload["state"] = to_state
    payload["revision"] = before + 1
    history = list(payload["transition_history"])
    history.append(
        TransitionRecord(
            action=action,
            from_state=session.state,
            to_state=to_state,
            revision_before=before,
            revision_after=before + 1,
            occurred_at=_utc_now(),
            reason=reason,
        ).model_dump(mode="python")
    )
    payload["transition_history"] = history
    return _rehash_session(payload)


def _require_state(session: SimulationSession, action: str, allowed: set[str]) -> None:
    if session.state not in allowed:
        raise SessionActionError(f"{action} is not legal from state {session.state}")


def _session_id() -> str:
    return f"session-{uuid4().hex[:20]}"


def make_tuning_profile(
    controller: ControllerRuntimeSpec,
    *,
    tunable_parameters: Sequence[str],
    parameter_bindings: Mapping[str, str],
    open_loop_behavior: Literal["stable", "unstable"],
    step_fraction: float = 0.05,
    bounds: Mapping[str, tuple[float, float]] | None = None,
    stabilizing_directions: Mapping[str, Literal[-1, 1]] | None = None,
    zero_step_scales: Mapping[str, float] | None = None,
    profile_id: str = "stability-only-v1",
) -> TuningProfile:
    """Create a finite, architecture-bound tuning profile."""

    if set(tunable_parameters) != set(parameter_bindings):
        raise ProposalValidationError(
            "parameter bindings must match the exact tuning whitelist"
        )
    if len(tunable_parameters) != len(set(tunable_parameters)):
        raise ProposalValidationError("tuning whitelist must be unique")
    allowed = _allowed_bindings(controller)
    rules: list[TuningParameterRule] = []
    for name in tunable_parameters:
        binding = parameter_bindings[name]
        if binding not in allowed:
            raise ProposalValidationError(
                f"binding is not valid for this controller: {binding}"
            )
        value = _read_binding(controller, binding)
        if bounds and name in bounds:
            lower, upper = bounds[name]
        else:
            scale = max(abs(value), 1.0)
            lower, upper = -10.0 * scale, 10.0 * scale
        direction = (
            stabilizing_directions[name]
            if stabilizing_directions and name in stabilizing_directions
            else (-1 if value < 0.0 else 1)
        )
        zero_scale = (
            zero_step_scales.get(name) if zero_step_scales is not None else None
        )
        rules.append(
            TuningParameterRule(
                name=name,
                binding=binding,
                lower_bound=lower,
                upper_bound=upper,
                stabilizing_direction=direction,
                zero_step_scale=zero_scale,
            )
        )
    return TuningProfile(
        profile_id=profile_id,
        open_loop_behavior=open_loop_behavior,
        step_fraction=step_fraction,
        parameters=rules,
    )


def create_free_input_session(
    *,
    pending_model: ExecutableModelSpec | None = None,
    model_assumptions: Sequence[str] = (),
) -> SimulationSession:
    """Start a free-input session at the mandatory model-review gate."""

    return SimulationSession(
        session_id=_session_id(),
        revision=0,
        origin="llm_proposed_model_hypothesis",
        evidence_boundary="llm_proposed_model_hypothesis",
        pending_model=pending_model,
        model_assumptions=list(model_assumptions),
        state="model_review",
    )


def create_stage5_session(
    *,
    source_run_id: str,
    source_plant_id: str,
    source_controller_architecture: str,
    source_link_sha256: str,
    model: ExecutableModelSpec,
    controller: ControllerRuntimeSpec,
    tuning_profile: TuningProfile,
    run_config: SimulationRunConfig,
    model_assumptions: Sequence[str] = (),
) -> SimulationSession:
    """Queue a fifth-stage candidate against its already compiled model."""

    reviewed = SimulationSession(
        session_id=_session_id(),
        revision=0,
        origin="stage5_candidate_model",
        evidence_boundary="stage5_candidate_model",
        source_run_id=source_run_id,
        source_plant_id=source_plant_id,
        source_controller_architecture=source_controller_architecture,
        source_link_sha256=source_link_sha256,
        pending_model=model,
        confirmed_model=model,
        model_assumptions=list(model_assumptions),
        model_confirmed=True,
        state="controller_ready",
    )
    return set_initial_controller(
        reviewed,
        controller,
        tuning_profile=tuning_profile,
        run_config=run_config,
        expected_revision=reviewed.revision,
    )


def create_discovery_simulation_session(
    *,
    source_run_id: str,
    source_plant_id: str,
    source_candidate_plant_id: str | None,
    source_controller_architecture: str,
    source_link_sha256: str,
    model: ExecutableModelSpec,
    controller: ControllerRuntimeSpec,
    tuning_profile: TuningProfile,
    run_config: SimulationRunConfig,
    model_assumptions: Sequence[str] = (),
) -> SimulationSession:
    """Queue a Stage-5 controller against a user-confirmed LLM model."""

    reviewed = SimulationSession(
        session_id=_session_id(),
        revision=0,
        origin="stage5_candidate_llm_model",
        evidence_boundary="llm_proposed_model_hypothesis",
        source_run_id=source_run_id,
        source_plant_id=source_plant_id,
        source_candidate_plant_id=source_candidate_plant_id,
        source_controller_architecture=source_controller_architecture,
        source_link_sha256=source_link_sha256,
        pending_model=model,
        confirmed_model=model,
        model_assumptions=list(model_assumptions),
        model_confirmed=True,
        state="controller_ready",
    )
    return set_initial_controller(
        reviewed,
        controller,
        tuning_profile=tuning_profile,
        run_config=run_config,
        expected_revision=reviewed.revision,
    )


def set_pending_model(
    session: SimulationSession,
    model: ExecutableModelSpec,
    *,
    assumptions: Sequence[str] = (),
    expected_revision: int | None = None,
) -> SimulationSession:
    _expect_revision(session, expected_revision)
    _require_state(session, "set_pending_model", {"model_review"})
    if session.origin != "llm_proposed_model_hypothesis":
        raise SessionActionError("only LLM-proposed model hypotheses can be replaced")
    return _transition(
        session,
        to_state="model_review",
        action="set_pending_model",
        updates={
            "pending_model": deepcopy(model),
            "confirmed_model": None,
            "model_confirmed": False,
            "model_assumptions": list(assumptions),
            "termination_reason": None,
        },
    )


def confirm_model(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    _expect_revision(session, expected_revision)
    _require_state(session, "confirm_model", {"model_review"})
    if session.pending_model is None:
        raise SessionActionError("no complete pending model to confirm")
    return _transition(
        session,
        to_state="controller_ready",
        action="confirm_model",
        reason=(
            "model confirmed for software simulation only; this does not "
            "validate a real object or hardware"
        ),
        updates={
            "confirmed_model": session.pending_model,
            "model_confirmed": True,
            "termination_reason": None,
        },
    )


def set_initial_controller(
    session: SimulationSession,
    controller: ControllerRuntimeSpec | None = None,
    *,
    tuning_profile: TuningProfile | None = None,
    run_config: SimulationRunConfig | None = None,
    expected_revision: int | None = None,
) -> SimulationSession:
    """Lock the initial architecture and queue its first trial."""

    _expect_revision(session, expected_revision)
    _require_state(session, "set_initial_controller", {"controller_ready"})
    selected = controller or session.initial_controller
    profile = tuning_profile or session.tuning_profile
    configuration = run_config or session.run_config
    if selected is None or profile is None or configuration is None:
        raise SessionActionError(
            "controller, tuning profile, and run configuration are required"
        )
    # Exact extraction validates every binding before the controller is locked.
    extract_tunable_parameters(selected, profile)
    return _transition(
        session,
        to_state="trial_pending",
        action="set_initial_controller",
        updates={
            "initial_controller": selected,
            "current_safe_controller": selected,
            "trial_controller": selected,
            "tuning_profile": profile,
            "run_config": configuration,
            "pending_proposal": None,
            "termination_reason": None,
        },
    )


def edit_initial_controller_parameters(
    session: SimulationSession,
    parameters: Mapping[str, float],
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    """Edit only the queued fifth-stage controller before its first trial."""

    _expect_revision(session, expected_revision)
    if (
        session.state != "trial_pending"
        or session.trials
        or session.pending_proposal is not None
    ):
        raise SessionActionError(
            "initial controller parameters may only be edited before the first trial"
        )
    if session.trial_controller is None or session.tuning_profile is None:
        raise SessionActionError("session has no editable initial controller")
    rebuilt = rebuild_controller(
        session.trial_controller,
        session.tuning_profile,
        parameters,
    )
    return _transition(
        session,
        to_state="trial_pending",
        action="edit_initial_controller_parameters",
        updates={
            "trial_controller": rebuilt,
            "pending_proposal": None,
            "termination_reason": None,
        },
    )


queue_initial_trial = set_initial_controller


def append_llm_call(
    session: SimulationSession,
    record: LLMCallRecord,
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    """Append an already-sanitized typed audit record without changing state."""

    _expect_revision(session, expected_revision)
    if session.state in TERMINAL_STATES:
        raise SessionActionError(
            f"append_llm_call is not legal from terminal state {session.state}"
        )
    allowed_states = (
        {"model_review"}
        if record.operation == "model_proposal"
        else {"needs_adjustment", "rolled_back"}
    )
    if session.state not in allowed_states:
        raise SessionActionError(
            f"{record.operation} audit is not legal from {session.state}"
        )
    payload = list(session.llm_calls)
    payload.append(record)
    return _transition(
        session,
        to_state=session.state,
        action="append_llm_call",
        updates={"llm_calls": payload},
    )


def _default_runner(
    session: SimulationSession,
    model: ExecutableModelSpec,
    controller: ControllerRuntimeSpec,
) -> Any:
    if session.run_config is None:
        raise SessionActionError("session has no simulation run configuration")
    config = session.run_config
    if isinstance(model, RegisteredNonlinearModelSpec):
        if not isinstance(controller, RegisteredControllerSpec):
            raise SessionActionError(
                "registered nonlinear model requires a registered controller"
            )
        from cfdc.sim.registered_runtime import run_registered_validation

        return run_registered_validation(
            model,
            controller,
            state_bounds=config.state_bounds or None,
        )
    from cfdc.sim.closed_loop_runtime import run_linear_closed_loop

    return run_linear_closed_loop(
        model,
        controller,
        reference=config.reference,
        horizon_s=config.horizon_s,
        sample_time_s=config.sample_time_s,
        actuator_bounds=config.actuator_bounds,
        state_bounds=config.state_bounds,
        output_bounds=config.output_bounds,
    )


def _normalize_runner_result(
    result: Any,
) -> tuple[list[SimulationTrace], StabilityDecision]:
    if isinstance(result, tuple) and len(result) == 2:
        raw_traces, raw_decision = result
    elif hasattr(result, "stability"):
        raw_decision = result.stability
        if hasattr(result, "traces"):
            raw_traces = result.traces
        elif hasattr(result, "trace"):
            raw_traces = [result.trace]
        else:
            raise ValueError("runner result has no trace payload")
    else:
        raise ValueError("runner returned an unsupported result")
    if isinstance(raw_traces, Mapping):
        trace_values = list(raw_traces.values())
    elif isinstance(raw_traces, Sequence) and not isinstance(
        raw_traces, (str, bytes, bytearray)
    ):
        trace_values = list(raw_traces)
    else:
        trace_values = [raw_traces]
    if not trace_values or len(trace_values) > 5:
        raise ValueError("runner must return one to five traces")
    traces = [
        SimulationTrace.model_validate(
            item.model_dump(mode="python") if hasattr(item, "model_dump") else item
        )
        for item in trace_values
    ]
    decision = StabilityDecision.model_validate(
        raw_decision.model_dump(mode="python")
        if hasattr(raw_decision, "model_dump")
        else raw_decision
    )
    return traces, decision


def _empty_failure_trace() -> SimulationTrace:
    return SimulationTrace(
        time_s=[],
        reference={"unavailable": []},
        outputs={"unavailable": []},
        requested_controls={"unavailable": []},
        applied_controls={"unavailable": []},
        events=[],
    )


def _runner_failure_decision(
    model: ExecutableModelSpec,
    reason: str,
    *,
    status: Literal["unstable", "inconclusive"] = "inconclusive",
) -> StabilityDecision:
    reason = reason[:1000] or "runner validation failed"
    is_hard = status == "unstable"
    is_discrete = (
        model.kind != "registered_nonlinear" and model.time_domain == "discrete"
    )
    if model.kind == "registered_nonlinear":
        scenario_ids = (
            [
                "angle_positive",
                "angle_negative",
                "position_and_angle_positive",
                "position_and_angle_negative",
                "mixed_velocity",
            ]
            if model.template_id == "underactuated_cartpole"
            else [
                "lateral_position",
                "altitude",
                "pitch",
                "combined_positive",
                "combined_negative",
            ]
        )
        scenario_evidence = [
            NonlinearScenarioEvidence(
                scenario_id=scenario_id,
                passed=False,
                trajectory_finite=False,
                trajectory_bounded=False,
                tail_error_envelope_contraction=-1.0,
                saturation_fraction=0.0,
                hard_failure=is_hard,
                sample_count=0,
                violations=[reason],
                evidence=[reason],
            )
            for scenario_id in scenario_ids
        ]
        pole_count = 4 if model.template_id == "underactuated_cartpole" else 6
        return StabilityDecision(
            status=status,
            analysis_domain="continuous",
            pole_analysis_method="registered_nonlinear_local_linearization",
            registered_template_id=model.template_id,
            poles=[ComplexValue(real=0.0, imaginary=0.0)] * pole_count,
            trajectory_finite=False,
            trajectory_bounded=False,
            tail_error_envelope_contraction=-1.0,
            saturation_fraction=0.0,
            hard_failure=is_hard,
            violations=[reason],
            evidence=[reason],
            scenario_evidence=scenario_evidence,
        )
    return StabilityDecision(
        status=status,
        analysis_domain="discrete" if is_discrete else "continuous",
        pole_analysis_method=(
            "exact_discrete_interconnection"
            if is_discrete
            else "exact_continuous_interconnection"
        ),
        poles=[],
        spectral_radius=2.0 if is_discrete else None,
        trajectory_finite=False,
        trajectory_bounded=False,
        tail_error_envelope_contraction=-1.0,
        saturation_fraction=0.0,
        hard_failure=is_hard,
        violations=[reason],
        evidence=[reason],
    )


def stability_only_score(decision: StabilityDecision) -> float:
    """Return the documented normalized score used only for soft comparison."""

    if decision.analysis_domain == "continuous":
        if decision.poles:
            margin = -(max(pole.real for pole in decision.poles) + 1e-6)
        else:
            margin = -1.0
    else:
        radius = (
            decision.spectral_radius if decision.spectral_radius is not None else 2.0
        )
        margin = 1.0 - 1e-6 - radius
    normalized_margin = margin / (1.0 + abs(margin))
    contraction = min(1.0, max(-1.0, decision.tail_error_envelope_contraction))
    return normalized_margin + 0.25 * contraction - 0.25 * decision.saturation_fraction


def _hard_violation(
    traces: Sequence[SimulationTrace], decision: StabilityDecision
) -> tuple[bool, str | None]:
    hard_events = [
        event
        for trace in traces
        for event in trace.events
        if event.kind in {"non_finite", "hard_bound_violation"}
    ]
    hard = decision.hard_failure or not decision.trajectory_finite or bool(hard_events)
    if not hard:
        return False, None
    reasons = list(decision.violations)
    reasons.extend(event.message for event in hard_events)
    return True, "; ".join(dict.fromkeys(reasons))[:2000] or "hard violation"


def _make_trial(
    *,
    iteration: int,
    controller: ControllerRuntimeSpec,
    proposal: ParameterProposal | None,
    traces: list[SimulationTrace],
    original_sample_counts: list[int],
    decision: StabilityDecision,
    creation_source: Literal["initial", "deterministic", "llm", "manual_restore"],
    hard_violation: bool,
    rolled_back: bool,
    rollback_reason: str | None,
) -> TrialRecord:
    occurred_at = _utc_now()
    payload = {
        "schema_version": "trial_record/v1",
        "iteration": iteration,
        "controller": controller,
        "proposal": proposal,
        "traces": traces,
        "original_sample_counts": original_sample_counts,
        "trace_storage_policy": (
            "deterministic_decimation_64"
            if any(
                original > len(trace.time_s)
                for original, trace in zip(original_sample_counts, traces)
            )
            else "full"
        ),
        "stability": decision,
        "creation_source": creation_source,
        "hard_violation": hard_violation,
        "rolled_back": rolled_back,
        "rollback_reason": rollback_reason,
        "stability_score": stability_only_score(decision),
        "occurred_at": occurred_at,
    }
    return TrialRecord(
        **payload,
        trial_hash=_sha256(payload),
    )


def _decimate_trace(
    trace: SimulationTrace, maximum_samples: int = 64
) -> SimulationTrace:
    sample_count = len(trace.time_s)
    if sample_count <= maximum_samples:
        return trace
    indices = sorted(
        {
            round(index * (sample_count - 1) / (maximum_samples - 1))
            for index in range(maximum_samples)
        }
    )

    def channels(values: Mapping[str, list[float]]) -> dict[str, list[float]]:
        return {
            name: [samples[index] for index in indices]
            for name, samples in values.items()
        }

    return SimulationTrace(
        time_s=[trace.time_s[index] for index in indices],
        reference=channels(trace.reference),
        states=channels(trace.states),
        outputs=channels(trace.outputs),
        requested_controls=channels(trace.requested_controls),
        applied_controls=channels(trace.applied_controls),
        events=list(trace.events),
    )


def run_next_trial(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
    runner: SimulationRunner | None = None,
    result_guard: SimulationResultGuard | None = None,
) -> SimulationSession:
    """Run one queued controller and stop immediately on first stability."""

    _expect_revision(session, expected_revision)
    _require_state(session, "run_next_trial", {"trial_pending"})
    if (
        session.confirmed_model is None
        or session.trial_controller is None
        or session.current_safe_controller is None
        or session.tuning_profile is None
    ):
        raise SessionActionError("pending trial is incomplete")
    evaluating = _transition(
        session,
        to_state="evaluating",
        action="begin_trial",
    )
    model = evaluating.confirmed_model
    controller = evaluating.trial_controller
    assert model is not None and controller is not None
    infrastructure_failure = False
    try:
        raw_result = (
            runner(deepcopy(model), deepcopy(controller))
            if runner is not None
            else _default_runner(evaluating, model, controller)
        )
        full_traces, decision = _normalize_runner_result(raw_result)
        if result_guard is not None:
            full_traces, decision = result_guard(
                full_traces,
                decision,
            )
    except Exception as exc:  # fail closed into auditable inconclusive evidence
        safe_reason = f"simulation runner rejected the trial: {type(exc).__name__}"
        full_traces = [_empty_failure_trace()]
        description = str(exc).casefold()
        nonfinite = any(
            marker in description
            for marker in ("non-finite", "finite_number", "nan", "infinity")
        )
        decision = _runner_failure_decision(
            model,
            safe_reason,
            status="unstable" if nonfinite else "inconclusive",
        )
        infrastructure_failure = not nonfinite

    validity_boundary = any(
        event.kind == "model_validity_boundary_violation"
        for trace in full_traces
        for event in trace.events
    )
    hard, rollback_reason = _hard_violation(full_traces, decision)
    if infrastructure_failure:
        hard, rollback_reason = False, None
    original_sample_counts = [len(trace.time_s) for trace in full_traces]
    traces = [_decimate_trace(trace) for trace in full_traces]
    attached_proposal = evaluating.pending_proposal
    if attached_proposal is None:
        creation_source: Literal[
            "initial", "deterministic", "llm", "manual_restore"
        ] = "initial" if not evaluating.trials else "manual_restore"
    else:
        creation_source = attached_proposal.source
    trial = _make_trial(
        iteration=len(evaluating.trials) + 1,
        controller=controller,
        proposal=attached_proposal,
        traces=traces,
        original_sample_counts=original_sample_counts,
        decision=decision,
        creation_source=creation_source,
        hard_violation=hard,
        rolled_back=hard,
        rollback_reason=rollback_reason,
    )
    trials = [*evaluating.trials, trial]
    soft_count = evaluating.soft_worsening_count
    if hard:
        soft_count = 0
    elif len(trials) >= 2:
        previous = trials[-2]
        soft_count = (
            soft_count + 1
            if trial.stability_score < previous.stability_score - 1e-12
            else 0
        )
    else:
        soft_count = 0

    safe_controller = evaluating.current_safe_controller
    trial_controller = controller
    termination_reason: str | None = None
    if decision.status == "stable":
        outcome: SessionState = "stable"
        safe_controller = controller
        termination_reason = (
            "current software/hypothesis model first satisfied the stability "
            "criteria; no performance optimization was run"
        )
    elif validity_boundary:
        outcome = "inconclusive"
        termination_reason = (
            "轨迹离开已确认的局部模型有效范围；模型有效范围失效，"
            "不能继续评价或调整控制器。"
        )
    elif hard:
        outcome = "rolled_back"
        trial_controller = safe_controller
        termination_reason = rollback_reason
    elif decision.status == "inconclusive":
        if infrastructure_failure:
            outcome = "inconclusive"
            termination_reason = (
                "simulation infrastructure failed to produce usable evidence"
            )
        else:
            outcome = "needs_adjustment"
    else:
        safe_controller = controller
        if soft_count >= 2:
            outcome = "frozen"
            termination_reason = "two consecutive soft stability worsenings"
        else:
            outcome = "needs_adjustment"

    if len(trials) >= evaluating.tuning_profile.max_trials and outcome not in {
        "stable",
        "inconclusive",
        "frozen",
    }:
        outcome = "budget_exhausted"
        termination_reason = "20-trial stability budget exhausted"

    return _transition(
        evaluating,
        to_state=outcome,
        action="complete_trial",
        reason=termination_reason,
        updates={
            "trials": trials,
            "current_safe_controller": safe_controller,
            "trial_controller": trial_controller,
            "pending_proposal": None,
            "soft_worsening_count": soft_count,
            "termination_reason": termination_reason,
        },
    )


run_next = run_next_trial


def _proposal_matches_current(
    session: SimulationSession, proposal: ParameterProposal
) -> None:
    _validate_proposal_checksum(proposal)
    if (
        session.trial_controller is None
        or session.tuning_profile is None
        or proposal.session_id != session.session_id
    ):
        raise ProposalValidationError("proposal/session identity mismatch")
    if proposal.base_trial_iteration != len(session.trials):
        raise ProposalValidationError("proposal base trial is stale")
    if proposal.architecture_sha256 != _architecture_hash(
        session.trial_controller, session.tuning_profile
    ):
        raise ProposalValidationError("proposal architecture is stale")
    current = extract_tunable_parameters(
        session.trial_controller, session.tuning_profile
    )
    if _canonical_json(current) != _canonical_json(proposal.old_parameters):
        raise ProposalValidationError("proposal old parameters are stale")
    # Re-run all bounds, zero, 10%, and architecture checks.
    rebuilt = rebuild_controller(
        session.trial_controller,
        session.tuning_profile,
        proposal.new_parameters,
    )
    rebuilt_parameters = extract_tunable_parameters(rebuilt, session.tuning_profile)
    rules = {item.name: item for item in session.tuning_profile.parameters}
    for name, new_value in rebuilt_parameters.items():
        relative = _relative_change(current[name], new_value, rules[name])
        if relative > 0.10 + 1e-12 or not math.isclose(
            relative,
            proposal.relative_change[name],
            rel_tol=1e-10,
            abs_tol=1e-12,
        ):
            raise ProposalValidationError(
                f"proposal relative change is invalid for {name}"
            )


def _terminate_inconclusive(
    session: SimulationSession, reason: str
) -> SimulationSession:
    return _transition(
        session,
        to_state="inconclusive",
        action="no_legal_stability_step",
        reason=reason,
        updates={"termination_reason": reason, "pending_proposal": None},
    )


def propose_deterministic_update(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    """Create and apply one deterministic 5%-10% stability-only update."""

    _expect_revision(session, expected_revision)
    _require_state(
        session,
        "propose_deterministic_update",
        {"needs_adjustment", "rolled_back"},
    )
    if (
        session.pending_proposal is not None
        and session.pending_proposal.approval_state == "pending"
    ):
        raise SessionActionError(
            "resolve the pending LLM proposal before deterministic tuning"
        )
    if session.trial_controller is None or session.tuning_profile is None:
        raise SessionActionError("session has no tunable controller")
    profile = session.tuning_profile
    current = extract_tunable_parameters(session.trial_controller, profile)
    latest = session.trials[-1] if session.trials else None
    reduce_magnitude = profile.open_loop_behavior == "stable" or (
        latest is not None
        and (latest.hard_violation or latest.stability.saturation_fraction > 0.10)
    )
    proposed: dict[str, float] = {}
    for rule in profile.parameters:
        old = current[rule.name]
        if reduce_magnitude:
            value = old * (1.0 - profile.step_fraction)
        elif old == 0.0:
            if rule.zero_step_scale is None:
                value = 0.0
            else:
                value = (
                    rule.stabilizing_direction
                    * rule.zero_step_scale
                    * profile.step_fraction
                )
        else:
            value = old + (
                rule.stabilizing_direction * abs(old) * profile.step_fraction
            )
        value = 0.0 if value == 0.0 else value
        if not rule.lower_bound <= value <= rule.upper_bound:
            return _terminate_inconclusive(
                session,
                f"no complete legal deterministic step: {rule.name} bound",
            )
        proposed[rule.name] = value
    if _canonical_json(proposed) == _canonical_json(current):
        return _terminate_inconclusive(
            session,
            "no complete legal deterministic step for zero/bounded gains",
        )
    rationale = (
        "Reduce gain magnitudes after hard/saturation evidence or on the "
        "declared open-loop-stable profile."
        if reduce_magnitude
        else "Move each whitelisted gain in its declared stabilizing direction."
    )
    proposal = build_parameter_proposal(
        session,
        source="deterministic",
        new_parameters=proposed,
        rationale=rationale,
    )
    _proposal_matches_current(session, proposal)
    controller = rebuild_controller(
        session.trial_controller, profile, proposal.new_parameters
    )
    return _transition(
        session,
        to_state="trial_pending",
        action="apply_deterministic_proposal",
        reason=rationale,
        updates={
            "trial_controller": controller,
            "pending_proposal": proposal,
            "termination_reason": None,
        },
    )


def register_llm_proposal(
    session: SimulationSession,
    *,
    new_parameters: Mapping[str, float],
    rationale: str,
    llm_call_record: LLMCallRecord | None = None,
    expected_revision: int | None = None,
) -> SimulationSession:
    """Register one constrained LLM suggestion without applying it."""

    _expect_revision(session, expected_revision)
    _require_state(
        session,
        "register_llm_proposal",
        {"needs_adjustment", "rolled_back"},
    )
    if (
        session.pending_proposal is not None
        and session.pending_proposal.approval_state == "pending"
    ):
        raise SessionActionError("one LLM proposal is already pending")
    if llm_call_record is not None and llm_call_record.operation != "gain_proposal":
        raise SessionActionError(
            "registered gain proposal requires a gain-proposal audit record"
        )
    proposal = build_parameter_proposal(
        session,
        source="llm",
        new_parameters=new_parameters,
        rationale=rationale,
    )
    _proposal_matches_current(session, proposal)
    return _transition(
        session,
        to_state="needs_adjustment",
        action="register_llm_proposal",
        updates={
            "pending_proposal": proposal,
            "llm_calls": (
                [*session.llm_calls, llm_call_record]
                if llm_call_record is not None
                else list(session.llm_calls)
            ),
        },
    )


def _proposal_with_state(
    proposal: ParameterProposal,
    approval_state: Literal["approved", "rejected", "stale"],
) -> ParameterProposal:
    payload = proposal.model_dump(mode="python")
    payload["approval_state"] = approval_state
    return ParameterProposal.model_validate(payload)


def approve_llm_proposal(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    """Explicitly approve exactly one still-current LLM proposal."""

    _expect_revision(session, expected_revision)
    _require_state(session, "approve_llm_proposal", {"needs_adjustment"})
    proposal = session.pending_proposal
    if (
        proposal is None
        or proposal.source != "llm"
        or proposal.approval_state != "pending"
    ):
        raise SessionActionError("there is no pending LLM proposal to approve")
    if proposal.base_revision + 1 != session.revision:
        stale = _proposal_with_state(proposal, "stale")
        return _transition(
            session,
            to_state="needs_adjustment",
            action="mark_llm_proposal_stale",
            reason="session revision changed after proposal registration",
            updates={"pending_proposal": stale},
        )
    _proposal_matches_current(session, proposal)
    assert session.trial_controller is not None
    assert session.tuning_profile is not None
    controller = rebuild_controller(
        session.trial_controller,
        session.tuning_profile,
        proposal.new_parameters,
    )
    approved = _proposal_with_state(proposal, "approved")
    return _transition(
        session,
        to_state="trial_pending",
        action="approve_llm_proposal",
        updates={
            "trial_controller": controller,
            "pending_proposal": approved,
            "termination_reason": None,
        },
    )


approve_parameter_proposal = approve_llm_proposal


def reject_llm_proposal(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    _expect_revision(session, expected_revision)
    _require_state(session, "reject_llm_proposal", {"needs_adjustment"})
    proposal = session.pending_proposal
    if (
        proposal is None
        or proposal.source != "llm"
        or proposal.approval_state != "pending"
    ):
        raise SessionActionError("there is no pending LLM proposal to reject")
    return _transition(
        session,
        to_state="needs_adjustment",
        action="reject_llm_proposal",
        updates={"pending_proposal": _proposal_with_state(proposal, "rejected")},
    )


reject_parameter_proposal = reject_llm_proposal


def rollback_session(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    """Manually restore the previous bounded controller snapshot."""

    _expect_revision(session, expected_revision)
    _require_state(
        session,
        "rollback_session",
        {"needs_adjustment", "trial_pending", "rolled_back"},
    )
    target = session.initial_controller
    for trial in reversed(session.trials[:-1]):
        if not trial.hard_violation:
            target = trial.controller
            break
    if target is None:
        raise SessionActionError("no safe controller snapshot is available")
    return _transition(
        session,
        to_state="rolled_back",
        action="manual_rollback",
        updates={
            "current_safe_controller": target,
            "trial_controller": target,
            "pending_proposal": None,
            "soft_worsening_count": 0,
            "termination_reason": "manual rollback to previous safe parameters",
        },
    )


def restore_safe_controller(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    _expect_revision(session, expected_revision)
    _require_state(
        session,
        "restore_safe_controller",
        {"needs_adjustment", "rolled_back", "trial_pending"},
    )
    if session.current_safe_controller is None:
        raise SessionActionError("no safe controller snapshot is available")
    return _transition(
        session,
        to_state="trial_pending",
        action="restore_safe_controller",
        updates={
            "trial_controller": session.current_safe_controller,
            "pending_proposal": None,
            "termination_reason": None,
        },
    )


def restore_initial_controller(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    """Queue the immutable fifth-stage controller snapshot again."""

    _expect_revision(session, expected_revision)
    _require_state(
        session,
        "restore_initial_controller",
        {"needs_adjustment", "rolled_back", "trial_pending"},
    )
    if session.initial_controller is None:
        raise SessionActionError("no initial controller snapshot is available")
    return _transition(
        session,
        to_state="trial_pending",
        action="restore_initial_controller",
        updates={
            "current_safe_controller": session.initial_controller,
            "trial_controller": session.initial_controller,
            "pending_proposal": None,
            "soft_worsening_count": 0,
            "termination_reason": None,
        },
    )


def cancel_session(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
) -> SimulationSession:
    _expect_revision(session, expected_revision)
    if session.state in TERMINAL_STATES:
        raise SessionActionError(
            f"cancel_session is not legal from state {session.state}"
        )
    return _transition(
        session,
        to_state="cancelled",
        action="cancel_session",
        reason="cancelled by user",
        updates={
            "pending_proposal": None,
            "termination_reason": "cancelled by user",
        },
    )


def run_deterministic_auto(
    session: SimulationSession,
    *,
    expected_revision: int | None = None,
    runner: SimulationRunner | None = None,
) -> SimulationSession:
    """Run only deterministic trial/update steps until the first terminal state."""

    _expect_revision(session, expected_revision)
    current = _copy_session(session)
    while current.state not in TERMINAL_STATES:
        if current.state == "trial_pending":
            current = run_next_trial(
                current,
                expected_revision=current.revision,
                runner=runner,
            )
        elif current.state in {"needs_adjustment", "rolled_back"}:
            current = propose_deterministic_update(
                current,
                expected_revision=current.revision,
            )
        else:
            raise SessionActionError(
                f"deterministic auto cannot proceed from {current.state}"
            )
    return current


def _validate_session_derived_integrity(session: SimulationSession) -> None:
    profile = session.tuning_profile
    if profile is not None and session.initial_controller is not None:
        initial_architecture = _architecture_hash(session.initial_controller, profile)
        extract_tunable_parameters(session.initial_controller, profile)
        for label, controller in (
            ("current_safe_controller", session.current_safe_controller),
            ("trial_controller", session.trial_controller),
        ):
            if controller is None:
                continue
            extract_tunable_parameters(controller, profile)
            if _architecture_hash(controller, profile) != initial_architecture:
                raise ValueError(f"{label} architecture changed")

    def validate_proposal_values(proposal: ParameterProposal) -> None:
        _validate_proposal_checksum(proposal)
        if profile is None:
            raise ValueError("proposal requires a tuning profile")
        if proposal.whitelist != profile.whitelist:
            raise ValueError("proposal whitelist/profile mismatch")
        rules = {item.name: item for item in profile.parameters}
        for name in proposal.whitelist:
            rule = rules[name]
            old = proposal.old_parameters[name]
            new = proposal.new_parameters[name]
            if not rule.lower_bound <= new <= rule.upper_bound:
                raise ValueError("proposal value is outside profile bounds")
            relative = _relative_change(old, new, rule)
            if relative > 0.10 + 1e-12 or not math.isclose(
                relative,
                proposal.relative_change[name],
                rel_tol=1e-10,
                abs_tol=1e-12,
            ):
                raise ValueError("proposal relative-change evidence mismatch")

    if session.pending_proposal is not None:
        validate_proposal_values(session.pending_proposal)
        if session.trial_controller is not None and profile is not None:
            if session.pending_proposal.approval_state in {
                "approved",
                "not_required",
            }:
                applied = extract_tunable_parameters(session.trial_controller, profile)
                if _canonical_json(applied) != _canonical_json(
                    session.pending_proposal.new_parameters
                ):
                    raise ValueError("applied pending proposal/controller mismatch")
    previous_controller = session.initial_controller
    for trial in session.trials:
        if trial.proposal is not None:
            validate_proposal_values(trial.proposal)
            if trial.proposal.source == "llm" and (
                trial.proposal.approval_state != "approved"
            ):
                raise ValueError("an executed LLM proposal must be approved")
        if profile is not None:
            # This also validates registered gain paths and matrix dimensions.
            trial_parameters = extract_tunable_parameters(trial.controller, profile)
            if session.initial_controller is not None and _architecture_hash(
                trial.controller, profile
            ) != _architecture_hash(session.initial_controller, profile):
                raise ValueError("trial controller architecture changed")
            if trial.proposal is not None:
                if _canonical_json(trial_parameters) != _canonical_json(
                    trial.proposal.new_parameters
                ):
                    raise ValueError("trial/proposal parameters mismatch")
                if previous_controller is not None:
                    previous = extract_tunable_parameters(previous_controller, profile)
                    if _canonical_json(previous) != _canonical_json(
                        trial.proposal.old_parameters
                    ):
                        raise ValueError("proposal base parameters mismatch")
        if not trial.hard_violation:
            previous_controller = trial.controller


def export_session(session: SimulationSession) -> str:
    """Export only the typed session envelope and its content checksum."""

    validated = SimulationSession.model_validate(session.model_dump(mode="python"))
    _validate_session_derived_integrity(validated)
    payload = validated.model_dump(mode="json")
    _scan_finite(payload)
    _scan_sensitive_keys(payload)
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    )


def _reject_constant(value: str) -> None:
    raise SessionImportError(f"non-finite JSON constant rejected: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SessionImportError(f"duplicate JSON key rejected: {key}")
        result[key] = value
    return result


def _verify_raw_content_hash(payload: Mapping[str, Any]) -> None:
    supplied = payload.get("content_sha256")
    if not isinstance(supplied, str):
        raise SessionImportError("session content_sha256 is required")
    expected = _sha256(_without(payload, "content_sha256"))
    if supplied != expected:
        raise SessionImportError("session content checksum mismatch")


def import_session(payload: str | bytes | bytearray) -> SimulationSession:
    """Verify and recover one typed session without invoking a runner or LLM."""

    raw_bytes = (
        bytes(payload)
        if isinstance(payload, (bytes, bytearray))
        else payload.encode("utf-8")
    )
    if len(raw_bytes) > _MAX_IMPORT_BYTES:
        raise SessionImportError("session import exceeds the 5 MB limit")
    try:
        decoded = raw_bytes.decode("utf-8")
        data = json.loads(
            decoded,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except SessionImportError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SessionImportError("invalid session JSON") from exc
    if not isinstance(data, dict):
        raise SessionImportError("session JSON must be one object")
    if data.get("schema_version") != "simulation_session/v1":
        raise SessionImportError("unsupported simulation session schema")
    if _json_depth(data) > _MAX_JSON_DEPTH:
        raise SessionImportError("session JSON nesting is too deep")
    try:
        _scan_finite(data)
        _scan_sensitive_keys(data)
        _verify_raw_content_hash(data)
    except ValueError as exc:
        raise SessionImportError(str(exc)) from exc

    if data.get("state") == "evaluating":
        # The original envelope was authenticated above.  Synchronous work is
        # never resumed implicitly after import.
        complete = all(
            data.get(name) is not None
            for name in (
                "confirmed_model",
                "trial_controller",
                "initial_controller",
                "current_safe_controller",
                "tuning_profile",
                "run_config",
            )
        )
        before = data.get("revision")
        history = data.get("transition_history")
        if not isinstance(before, int) or not isinstance(history, list):
            raise SessionImportError("invalid in-flight session history")
        to_state: SessionState = "trial_pending" if complete else "inconclusive"
        history.append(
            TransitionRecord(
                action="recover_inflight_import",
                from_state="evaluating",
                to_state=to_state,
                revision_before=before,
                revision_after=before + 1,
                occurred_at=_utc_now(),
                reason=(
                    "in-flight simulation was not resumed automatically"
                    if complete
                    else "in-flight session lacked a complete pending trial"
                ),
            ).model_dump(mode="json")
        )
        data["revision"] = before + 1
        data["state"] = to_state
        data["transition_history"] = history
        if not complete:
            data["termination_reason"] = (
                "in-flight imported session lacked a complete pending trial"
            )
        data["content_sha256"] = None
    try:
        session = SimulationSession.model_validate(data)
        _validate_session_derived_integrity(session)
    except (ValueError, TypeError) as exc:
        raise SessionImportError(f"invalid simulation session: {exc}") from exc
    return _copy_session(session)


def validate_session_mapping(
    payload: Mapping[str, Any],
) -> SimulationSession:
    """Validate an already-decoded trusted-transport state without file limits.

    This is used for the in-memory Gradio state.  Uploaded JSON must still go
    through :func:`import_session`, which additionally enforces byte limits,
    duplicate-key rejection, and in-flight recovery.
    """

    data = deepcopy(dict(payload))
    if data.get("schema_version") != "simulation_session/v1":
        raise SessionImportError("unsupported simulation session schema")
    try:
        _scan_finite(data)
        _scan_sensitive_keys(data)
        _verify_raw_content_hash(data)
        session = SimulationSession.model_validate(data)
        _validate_session_derived_integrity(session)
    except (ValueError, TypeError) as exc:
        raise SessionImportError(f"invalid simulation session: {exc}") from exc
    return _copy_session(session)


def make_llm_call_record(
    *,
    operation: Literal["model_proposal", "gain_proposal"],
    provider: str,
    model: str,
    messages: Sequence[LLMMessageRecord | Mapping[str, str]],
    structured_response: Mapping[str, Any] | None = None,
    invalid_raw_text: str | None = None,
    validation_status: Literal["accepted", "rejected", "need_more", "error"],
    validation_errors: Sequence[str] = (),
) -> LLMCallRecord:
    """Construct a hash-bound record from data that has already been sanitized."""

    typed_messages = [
        item
        if isinstance(item, LLMMessageRecord)
        else LLMMessageRecord.model_validate(item)
        for item in messages
    ]
    response = (
        dict(structured_response)
        if structured_response is not None
        else {"invalid_raw_text": invalid_raw_text or ""}
    )
    seed = {
        "operation": operation,
        "provider": provider,
        "model": model,
        "messages": [item.model_dump(mode="json") for item in typed_messages],
        "response": response,
        "occurred_at": _utc_now(),
    }
    call_hash = _sha256(seed)
    return LLMCallRecord(
        call_id=f"llm-{call_hash[:20]}",
        operation=operation,
        provider=provider,
        model=model,
        messages=typed_messages,
        structured_response=(
            dict(structured_response) if structured_response is not None else None
        ),
        invalid_raw_text=invalid_raw_text,
        validation_status=validation_status,
        validation_errors=list(validation_errors),
        request_sha256=_sha256(
            [item.model_dump(mode="json") for item in typed_messages]
        ),
        response_sha256=_sha256(response),
        occurred_at=seed["occurred_at"],
    )


__all__ = [
    "LLMCallRecord",
    "LLMMessageRecord",
    "ParameterProposal",
    "ProposalValidationError",
    "SessionActionError",
    "SessionImportError",
    "SessionState",
    "SimulationRunConfig",
    "SimulationRunner",
    "SimulationSession",
    "StaleRevisionError",
    "TERMINAL_STATES",
    "TransitionRecord",
    "TrialRecord",
    "TuningParameterRule",
    "TuningProfile",
    "append_llm_call",
    "approve_llm_proposal",
    "approve_parameter_proposal",
    "build_parameter_proposal",
    "cancel_session",
    "confirm_model",
    "controller_architecture_hash",
    "create_free_input_session",
    "create_discovery_simulation_session",
    "export_session",
    "extract_tunable_parameters",
    "import_session",
    "make_llm_call_record",
    "make_tuning_profile",
    "propose_deterministic_update",
    "rebuild_controller",
    "register_llm_proposal",
    "reject_llm_proposal",
    "reject_parameter_proposal",
    "restore_safe_controller",
    "rollback_session",
    "run_deterministic_auto",
    "run_next",
    "run_next_trial",
    "set_initial_controller",
    "set_pending_model",
    "stability_only_score",
    "validate_session_mapping",
]
