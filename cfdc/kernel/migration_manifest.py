"""Build-time migration manifest for the archived CFDC v3 workbench.

The manifest is intentionally data only.  Runtime imports never resolve a
module from ``archive``; a release engineer may pass an archive directory to
``build_migration_manifest`` to refresh source hashes during a migration.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .contracts import (
    CONTROLLER_IR_VERSION,
    EVIDENCE_SESSION_VERSION,
    FEATURE_ARTIFACT_VERSION,
    FREEZE_VERSION,
    IMPORT_REPORT_VERSION,
    MULTISTAGE_VERSION,
    OPERATOR_HANDOFF_VERSION,
    PACKET_VERSION,
    PROTOCOL_VERSION,
    QUALIFICATION_VERSION,
    TASK_CONTRACT_VERSION,
    TUNING_CONTRACT_VERSION,
    UPLOAD_AUDIT_VERSION,
)

MIGRATION_MANIFEST_VERSION = "cfdc-migration/v1"
PARITY_MATRIX_VERSION = "cfdc-v3-parity/v1"


@dataclass(frozen=True)
class MigrationItem:
    source: str
    target: str
    contract: str
    source_hash: str | None = None
    status: str = "migrated"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# These are explicit archive paths, rather than a repository glob.  The list
# records the implementation boundary without making the archive a runtime
# dependency or accidentally importing benchmarks, answers, or receipts.
MIGRATION_ITEMS: tuple[MigrationItem, ...] = (
    MigrationItem(
        "src/cfdc_session_events.py",
        "cfdc/kernel/session.py",
        EVIDENCE_SESSION_VERSION,
    ),
    MigrationItem(
        "src/cfdc_task_relevant_diagnostic_authority_v1.py",
        "cfdc/kernel/diagnostics.py",
        "cfdc-diagnostics/v2.0",
    ),
    MigrationItem(
        "src/cfdc_executor_workflow.py",
        "cfdc/kernel/service.py",
        TASK_CONTRACT_VERSION,
    ),
    MigrationItem(
        "src/task_type_contract.py",
        "cfdc/kernel/contracts.py",
        TASK_CONTRACT_VERSION,
    ),
    MigrationItem(
        "src/cfdc_interaction_budget.py",
        "cfdc/kernel/contracts.py",
        TASK_CONTRACT_VERSION,
    ),
    MigrationItem(
        "src/cfdc_route_packages.py",
        "cfdc/kernel/routes.py",
        "cfdc-route/v1",
    ),
    MigrationItem(
        "src/controller_freeze.py",
        "cfdc/kernel/contracts.py",
        FREEZE_VERSION,
    ),
    MigrationItem(
        "src/cfdc_multistage_contract.py",
        "cfdc/kernel/multistage.py",
        MULTISTAGE_VERSION,
    ),
    MigrationItem(
        "src/cfdc_transition_hold_runtime.py",
        "cfdc/kernel/multistage.py",
        MULTISTAGE_VERSION,
    ),
    MigrationItem(
        "src/multistage_controller_progression.py",
        "cfdc/kernel/multistage.py",
        MULTISTAGE_VERSION,
    ),
    MigrationItem(
        "src/cfdc_software_performance_judge_v1.py",
        "cfdc/kernel/service.py",
        PACKET_VERSION,
    ),
    MigrationItem(
        "src/cfdc_software_performance_projection.py",
        "cfdc/kernel/evaluation.py",
        PACKET_VERSION,
    ),
    MigrationItem(
        "src/initial_controller_qualification.py",
        "cfdc/kernel/service.py",
        FREEZE_VERSION,
    ),
    MigrationItem(
        "src/cfdc_software_performance_workflow_v1.py",
        "cfdc/kernel/service.py",
        PACKET_VERSION,
    ),
    MigrationItem(
        "src/bounded_simulation_tuning.py",
        "cfdc/kernel/tuning.py",
        TUNING_CONTRACT_VERSION,
    ),
    MigrationItem(
        "bounded_simulation_tuning_contract.json",
        "cfdc/kernel/tuning.py",
        TUNING_CONTRACT_VERSION,
    ),
    MigrationItem(
        "cfdc_bounded_performance_feedback_iteration_contract_v1.json",
        "cfdc/kernel/tuning.py",
        TUNING_CONTRACT_VERSION,
    ),
    # Runtime route registries and JSON schemas are part of the migrated
    # contract even though they are data resources rather than Python modules.
    # Keeping them explicit prevents a future route from being introduced only
    # by a name or a dynamically loaded JSON file without an implementation
    # review and a recorded source hash.
    MigrationItem(
        "src/control_route_registry.py",
        "cfdc/kernel/routes.py",
        "cfdc-route/v1",
    ),
    MigrationItem(
        "control_route_registry.json",
        "cfdc/kernel/routes.py",
        "cfdc-route/v1",
    ),
    MigrationItem(
        "control_route_extensions.json",
        "cfdc/kernel/routes.py",
        "cfdc-route/v1",
    ),
    MigrationItem(
        "unified_executor_capabilities.json",
        "cfdc/kernel/providers.py",
        "cfdc-provider/v1",
    ),
    MigrationItem(
        "cfdc_loop_schema.json",
        "cfdc/kernel/contracts.py",
        TASK_CONTRACT_VERSION,
    ),
    MigrationItem(
        "diagnostic_ledger_schema.json",
        "cfdc/kernel/diagnostics.py",
        "cfdc-diagnostics/v2.0",
    ),
    MigrationItem(
        "performance_evaluation_packet_schema.json",
        "cfdc/kernel/contracts.py",
        PACKET_VERSION,
    ),
    MigrationItem(
        "src/provisional_controller_ir.py",
        "cfdc/kernel/controllers.py",
        CONTROLLER_IR_VERSION,
    ),
    MigrationItem(
        "src/provisional_ir_contract.py",
        "cfdc/kernel/controllers.py",
        CONTROLLER_IR_VERSION,
    ),
    MigrationItem(
        "src/bounded_experiment_protocol.py",
        "cfdc/experiments/protocols.py",
        PROTOCOL_VERSION,
    ),
    MigrationItem(
        "src/build_physical_experiment_packet.py",
        "cfdc/experiments/operator.py",
        OPERATOR_HANDOFF_VERSION,
    ),
    MigrationItem(
        "src/nonexpert_upload_validation.py",
        "cfdc/evidence/ingestion.py",
        UPLOAD_AUDIT_VERSION,
    ),
    MigrationItem(
        "src/physical_experiment_preflight.py",
        "cfdc/evidence/physical.py",
        "cfdc-physical-preflight/v1",
    ),
    MigrationItem(
        "src/physical_unit_normalization.py",
        "cfdc/evidence/physical.py",
        "cfdc-engineering-units/v1",
    ),
    MigrationItem(
        "src/cfdc_core_feature_parameterization_v1.py",
        "cfdc/features/kernel.py",
        FEATURE_ARTIFACT_VERSION,
    ),
    MigrationItem(
        "src/task_bound_siso_initial_controller_adapter.py",
        "cfdc/controllers/kernel_synthesis.py",
        CONTROLLER_IR_VERSION,
    ),
    MigrationItem(
        "src/run_initial_controller_qualification_matrix.py",
        "cfdc/controllers/qualification.py",
        QUALIFICATION_VERSION,
    ),
    MigrationItem(
        "cfdc_physical_training_cases_v1.json",
        "cfdc/kernel/resources/physical_training_cases.v1.json",
        "cfdc-training-cases/v1",
    ),
    MigrationItem(
        "src/run_cfdc_physical_training_cases_v1.py",
        "cfdc/sim/training.py",
        "cfdc-training-provider/v1",
    ),
    MigrationItem(
        "src/run_cfdc_independent_provider_full_chain_acceptance_v20.py",
        "cfdc/kernel/providers.py",
        "cfdc-provider/v1",
    ),
    MigrationItem(
        "src/cfdc_llm_role_reliability_cases_v4.py",
        "cfdc/kernel/agents.py",
        "cfdc-agent-governance/v1",
    ),
    MigrationItem(
        "benchmarks/cfdc_canonical_v10/contract.json",
        "tests/test_kernel_v3_full.py",
        "cfdc-canonical-benchmark/v10",
    ),
    MigrationItem(
        "cfdc_benchmark_coverage_contract.json",
        "tests/test_kernel_v3_full.py",
        "cfdc-benchmark-coverage/v1",
    ),
    MigrationItem(
        "src/cfdc_canonical_session.py",
        "cfdc/kernel/importer.py",
        IMPORT_REPORT_VERSION,
    ),
)


PARITY_CAPABILITIES: tuple[dict[str, Any], ...] = (
    {
        "capability": "versioned_session_and_v3_import",
        "sources": ("src/cfdc_session_events.py", "src/cfdc_canonical_session.py"),
        "targets": ("cfdc/kernel/session.py", "cfdc/kernel/importer.py"),
        "contracts": (EVIDENCE_SESSION_VERSION, IMPORT_REPORT_VERSION),
        "tests": ("test_v3_import_is_read_only_safe_and_idempotent",),
    },
    {
        "capability": "experiment_protocol_and_operator_handoff",
        "sources": (
            "src/bounded_experiment_protocol.py",
            "src/build_physical_experiment_packet.py",
        ),
        "targets": ("cfdc/experiments/protocols.py", "cfdc/experiments/operator.py"),
        "contracts": (PROTOCOL_VERSION, OPERATOR_HANDOFF_VERSION),
        "tests": ("test_protocol_tampering_and_operator_bundle",),
    },
    {
        "capability": "protocol_bound_upload_gates",
        "sources": (
            "src/nonexpert_upload_validation.py",
            "external_experiment_packet_schema.json",
        ),
        "targets": ("cfdc/evidence/ingestion.py",),
        "contracts": (UPLOAD_AUDIT_VERSION,),
        "tests": ("test_upload_all_eight_gates_and_rejected_attempt_is_non_consuming",),
    },
    {
        "capability": "physical_preflight_and_units",
        "sources": (
            "src/physical_experiment_preflight.py",
            "src/physical_unit_normalization.py",
        ),
        "targets": ("cfdc/evidence/physical.py",),
        "contracts": ("cfdc-physical-preflight/v1",),
        "tests": ("test_physical_preflight_and_engineering_unit_normalization",),
    },
    {
        "capability": "automatic_feature_derivation",
        "sources": ("src/cfdc_core_feature_parameterization_v1.py",),
        "targets": ("cfdc/features/kernel.py",),
        "contracts": (FEATURE_ARTIFACT_VERSION,),
        "tests": ("test_registered_case_full_chain_reaches_independent_evaluation",),
    },
    {
        "capability": "route_registry_and_capability_gaps",
        "sources": (
            "control_route_registry.json",
            "control_route_extensions.json",
            "unified_executor_capabilities.json",
        ),
        "targets": (
            "cfdc/kernel/resources/control_route_registry.v2.7.1.json",
            "cfdc/kernel/routes.py",
        ),
        "contracts": ("cfdc-route/v1",),
        "tests": ("test_all_executable_controller_contracts_synthesize_and_qualify",),
    },
    {
        "capability": "controller_synthesis_and_qualification",
        "sources": (
            "src/task_bound_siso_initial_controller_adapter.py",
            "src/run_initial_controller_qualification_matrix.py",
        ),
        "targets": (
            "cfdc/controllers/kernel_synthesis.py",
            "cfdc/controllers/qualification.py",
        ),
        "contracts": (CONTROLLER_IR_VERSION, QUALIFICATION_VERSION),
        "tests": ("test_all_executable_controller_contracts_synthesize_and_qualify",),
    },
    {
        "capability": "independent_provider_evaluation",
        "sources": (
            "src/run_cfdc_independent_provider_full_chain_acceptance_v20.py",
            "performance_evaluation_packet_schema.json",
        ),
        "targets": ("cfdc/kernel/providers.py", "cfdc/kernel/service.py"),
        "contracts": ("cfdc-provider/v1", PACKET_VERSION),
        "tests": ("test_registered_case_full_chain_reaches_independent_evaluation",),
    },
    {
        "capability": "bounded_feedback_and_fresh_confirmation",
        "sources": (
            "src/cfdc_bounded_performance_feedback_iteration_v1.py",
            "cfdc_bounded_performance_feedback_iteration_contract_v1.json",
        ),
        "targets": ("cfdc/kernel/tuning.py", "cfdc/kernel/service.py"),
        "contracts": (TUNING_CONTRACT_VERSION,),
        "tests": ("test_feedback_creates_new_freeze_and_requires_fresh_confirmation",),
    },
    {
        "capability": "multi_agent_role_governance",
        "sources": (
            "src/cfdc_llm_role_reliability_cases_v4.py",
            "cfdc_llm_role_reliability_acceptance_contract_v4.json",
        ),
        "targets": ("cfdc/kernel/agents.py", "cfdc/kernel/replies.py"),
        "contracts": ("cfdc-agent-governance/v1",),
        "tests": (
            "test_kernel_agent_context_is_role_scoped_and_has_no_supervisor",
            "test_composite_adapter_revises_once_then_submits_only_after_critic_passes",
        ),
    },
    {
        "capability": "canonical_and_physical_training_governance",
        "sources": (
            "benchmarks/cfdc_canonical_v10/contract.json",
            "cfdc_physical_training_cases_v1.json",
            "cfdc_benchmark_coverage_contract.json",
        ),
        "targets": ("cfdc/kernel/cases.py", "cfdc/sim/training.py"),
        "contracts": ("cfdc-canonical-benchmark/v10", "cfdc-training-cases/v1"),
        "tests": (
            "test_case_catalog_has_five_training_six_transition_and_seven_audit_cases",
        ),
    },
)


def build_v3_parity_matrix(source_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(source_root).resolve() if source_root is not None else None
    rows: list[dict[str, Any]] = []
    for item in PARITY_CAPABILITIES:
        hashes: dict[str, str | None] = {}
        for source in item["sources"]:
            digest = None
            if root is not None:
                path = root / source
                if not path.is_file():
                    raise FileNotFoundError(f"parity_source_missing: {source}")
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
            hashes[source] = digest
        rows.append({**item, "source_hashes": hashes, "status": "migrated_and_tested"})
    value: dict[str, Any] = {
        "matrix_version": PARITY_MATRIX_VERSION,
        "rows": rows,
        "runtime_archive_dependency": False,
    }
    value["matrix_fingerprint"] = hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    return value


def build_migration_manifest(source_root: str | Path | None = None) -> dict[str, Any]:
    """Return an auditable manifest, optionally hashing explicit source files."""

    root = Path(source_root).resolve() if source_root is not None else None
    items: list[MigrationItem] = []
    for item in MIGRATION_ITEMS:
        source_hash = item.source_hash
        if root is not None:
            source_path = root / item.source
            if not source_path.is_file():
                raise FileNotFoundError(f"migration_source_missing: {item.source}")
            source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        items.append(
            MigrationItem(
                source=item.source,
                target=item.target,
                contract=item.contract,
                source_hash=source_hash,
                status=item.status,
            )
        )
    value: dict[str, Any] = {
        "manifest_version": MIGRATION_MANIFEST_VERSION,
        "target_workflow_version": "cfdc-v6-kernel/v1",
        "contracts": {
            "task": TASK_CONTRACT_VERSION,
            "session": EVIDENCE_SESSION_VERSION,
            "freeze": FREEZE_VERSION,
            "packet": PACKET_VERSION,
            "controller_ir": CONTROLLER_IR_VERSION,
            "multistage": MULTISTAGE_VERSION,
            "tuning": TUNING_CONTRACT_VERSION,
        },
        "items": [item.to_dict() for item in items],
        "runtime_archive_dependency": False,
    }
    value["manifest_fingerprint"] = hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    return value


__all__ = [
    "MIGRATION_ITEMS",
    "MIGRATION_MANIFEST_VERSION",
    "PARITY_CAPABILITIES",
    "PARITY_MATRIX_VERSION",
    "MigrationItem",
    "build_migration_manifest",
    "build_v3_parity_matrix",
]
