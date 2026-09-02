"""Evidence-driven CFDC kernel migrated from the archived v3 workbench."""

from cfdc.knowledge import KnowledgeContext, RetrievalRequest, RuleDecision

from .agents import AgentReviewBlocked, AgentRole, KernelAgentCoordinator
from .contracts import (
    CONTROLLER_IR_VERSION,
    DIAGNOSTIC_IDS,
    EVIDENCE_SESSION_VERSION,
    FREEZE_VERSION,
    MULTISTAGE_VERSION,
    PACKET_VERSION,
    SUPPORTED_TASK_TYPES,
    TUNING_CONTRACT_VERSION,
    UNSUPPORTED_TASK_TYPES,
    ControllerFreeze,
    EvaluationPacket,
    TaskContract,
    fingerprint,
)
from .controllers import (
    ControllerIR,
    validate_controller_family_for_route,
    validate_controller_for_route,
)
from .diagnostics import DiagnosticEntry, DiagnosticLedger, DiagnosticReadiness
from .migration_manifest import (
    MIGRATION_ITEMS,
    MIGRATION_MANIFEST_VERSION,
    PARITY_CAPABILITIES,
    PARITY_MATRIX_VERSION,
    MigrationItem,
    build_migration_manifest,
    build_v3_parity_matrix,
)
from .multistage import (
    MultiStagePlan,
    PhaseContract,
    compile_phase_plan,
    validate_handoff,
)
from .providers import (
    CallableEvaluationProvider,
    CallableExperimentProvider,
    CurrentModelExperimentProvider,
    EvaluationProvider,
    EvaluationProviderRegistry,
    ExperimentProvider,
    ProviderRegistry,
    PublicTrace,
    evidence_from_trace,
)
from .replies import (
    KernelReplyMode,
    build_kernel_input_contract,
    parse_kernel_json,
    prepare_kernel_reply,
)
from .routes import RouteCapability, resolve_route, route_capability
from .session import EvidenceSession, RegisteredCaseBinding, SessionEvent
from .tasks import (
    P1_1_TASK_SEMANTICS_VERSION,
    TASK_SUCCESS_METRICS,
    TaskTypeContractError,
    disturbance_event_fingerprint,
    evaluate_nominal_task_outcome,
    infer_task_type,
    task_success_requirements,
    transition_outcome_binding,
    validate_task_type_contract,
)
from .tuning import (
    TuningContract,
    TuningResult,
    bounded_parameter_candidates,
    run_bounded_tuning,
)

__all__ = [
    "CONTROLLER_IR_VERSION",
    "DIAGNOSTIC_IDS",
    "EVIDENCE_SESSION_VERSION",
    "FREEZE_VERSION",
    "MIGRATION_ITEMS",
    "MIGRATION_MANIFEST_VERSION",
    "MULTISTAGE_VERSION",
    "P1_1_TASK_SEMANTICS_VERSION",
    "PACKET_VERSION",
    "PARITY_CAPABILITIES",
    "PARITY_MATRIX_VERSION",
    "SUPPORTED_TASK_TYPES",
    "TASK_SUCCESS_METRICS",
    "TUNING_CONTRACT_VERSION",
    "UNSUPPORTED_TASK_TYPES",
    "AgentReviewBlocked",
    "AgentRole",
    "CallableEvaluationProvider",
    "CallableExperimentProvider",
    "ControllerFreeze",
    "ControllerIR",
    "CurrentModelExperimentProvider",
    "DiagnosticEntry",
    "DiagnosticLedger",
    "DiagnosticReadiness",
    "EvaluationPacket",
    "EvaluationProvider",
    "EvaluationProviderRegistry",
    "EvidenceSession",
    "ExperimentProvider",
    "KernelActionError",
    "KernelAgentCoordinator",
    "KernelReplyMode",
    "KnowledgeContext",
    "MigrationItem",
    "MultiStagePlan",
    "PhaseContract",
    "ProviderRegistry",
    "PublicTrace",
    "RegisteredCaseBinding",
    "RetrievalRequest",
    "RouteCapability",
    "RuleDecision",
    "SessionEvent",
    "TaskContract",
    "TaskTypeContractError",
    "TuningContract",
    "TuningResult",
    "WorkflowService",
    "bounded_parameter_candidates",
    "build_kernel_input_contract",
    "build_migration_manifest",
    "build_v3_parity_matrix",
    "compile_phase_plan",
    "disturbance_event_fingerprint",
    "evaluate_nominal_task_outcome",
    "evidence_from_trace",
    "fingerprint",
    "independent_judge",
    "infer_task_type",
    "parse_kernel_json",
    "prepare_kernel_reply",
    "resolve_route",
    "route_capability",
    "run_bounded_tuning",
    "task_success_requirements",
    "transition_outcome_binding",
    "validate_controller_family_for_route",
    "validate_controller_for_route",
    "validate_handoff",
    "validate_task_type_contract",
]


def __getattr__(name: str):
    """Load the orchestration service lazily to keep core contracts acyclic."""
    if name in {"KernelActionError", "WorkflowService", "independent_judge"}:
        from .service import KernelActionError, WorkflowService, independent_judge

        return {
            "WorkflowService": WorkflowService,
            "independent_judge": independent_judge,
            "KernelActionError": KernelActionError,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
