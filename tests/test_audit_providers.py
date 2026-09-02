"""Regression coverage for independent public audit providers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cfdc.experiments.protocols import compile_protocol
from cfdc.kernel.cases import AUDIT_CASES, public_case_catalog, public_training_case
from cfdc.kernel.contracts import TaskContract
from cfdc.kernel.service import WorkflowService
from cfdc.sim.training import build_training_provider_registries

_EXPECTED_ROUTE_FAMILIES = {
    "audit_class_i_level": "PI",
    "audit_class_ii_thermal": "two_dof_pid",
    "audit_class_ii_oscillator": "two_dof_pid",
    "audit_class_iii_motion": "PD_integrator",
    "audit_class_iv_nmp": "two_dof_PI",
    "audit_class_iv_high_order": "phase_guarded_2dof_PI",
    "audit_class_v_mimo": "decentralized_channel_PI",
}


def _diagnostics(case_id: str) -> dict[str, dict[str, object]]:
    assessments = {
        "open_loop_stability": "stable",
        "nonminimum_phase": "minimum_phase",
        "significant_delay": "not_significant",
        "relative_degree": "low",
        "sensing_actuation_adequacy": "adequate",
        "nonlinearity_strength": "weak",
        "coupling_underactuation": "siso",
        "uncertainty_variation": "small",
    }
    overrides = {
        "audit_class_ii_thermal": {"relative_degree": "order2"},
        "audit_class_ii_oscillator": {"relative_degree": "order2"},
        "audit_class_iii_motion": {"open_loop_stability": "marginal"},
        "audit_class_iv_nmp": {"nonminimum_phase": "nonminimum_phase"},
        "audit_class_iv_high_order": {"relative_degree": "high"},
        "audit_class_v_mimo": {"coupling_underactuation": "severe_mimo"},
    }
    values = {**assessments, **overrides.get(case_id, {})}
    return {
        key: {
            "status": "known",
            "assessment": assessment,
            "evidence": "public operator observation",
            "confidence": 0.95,
        }
        for key, assessment in values.items()
    }


def test_audit_catalog_uses_seven_independent_public_tasks() -> None:
    catalog = public_case_catalog()

    assert len(AUDIT_CASES) == 7
    assert {catalog[case_id]["kind"] for case_id in AUDIT_CASES} == {"audit"}
    assert all("provider_case_id" not in catalog[case_id] for case_id in AUDIT_CASES)
    assert all(
        "base_case_id" not in public_training_case(case_id) for case_id in AUDIT_CASES
    )
    assert (
        len(
            {
                public_training_case(case_id)["task"]["description"]
                for case_id in AUDIT_CASES
            }
        )
        == 7
    )


def test_audit_provider_has_no_legacy_or_controller_dependency() -> None:
    source = Path("cfdc/sim/audit.py").read_text(encoding="utf-8")

    assert "archive/" not in source
    assert "route_catalog" not in source
    assert "controllers." not in source
    assert "receipt" not in source.casefold()


def test_audit_provider_ids_and_public_traces_are_case_distinct() -> None:
    provider_ids: set[str] = set()
    evaluation_ids: set[str] = set()
    trace_fingerprints: set[str] = set()
    response_signatures: set[tuple[float, float, float]] = set()

    for case_id in AUDIT_CASES:
        task = TaskContract.from_user_input(public_training_case(case_id)["task"])
        identification, identification_id, _, evaluation_id = (
            build_training_provider_registries(case_id)
        )
        provider = identification.get(identification_id)
        protocol = compile_protocol(
            task,
            {"route_id": "test", "experiment_primitives": ["bounded_input_sequence"]},
            provider={
                "provider_id": provider.provider_id,
                "provider_version": provider.provider_version,
                "capabilities": provider.capabilities,
            },
            request={
                "operation": "bounded_input_sequence",
                "segments": [
                    {"duration_s": 2.0, "input_value": 0.0},
                    {"duration_s": 2.0, "input_value": 0.4},
                    {"duration_s": 2.0, "input_value": -0.2},
                    {"duration_s": 2.0, "input_value": 0.0},
                ],
                "repeats": 3,
                "sample_period_s": 0.02,
                "requested_signals": list(task.measured_signals),
                "control_inputs": list(task.control_inputs or (task.control_input,)),
            },
        ).to_dict()
        traces = provider.execute(protocol, task=task.to_dict())

        provider_ids.add(identification_id)
        evaluation_ids.add(evaluation_id)
        trace_fingerprints.add(traces[0].fingerprint)
        response = traces[0].signals[task.measured_signals[0]]
        response_signatures.add(
            (round(min(response), 5), round(max(response), 5), round(response[-1], 5))
        )
        public = json.dumps([trace.to_dict() for trace in traces], ensure_ascii=False)
        assert "controller" not in public.casefold()
        assert "expected_route" not in public
        assert "private" not in public.casefold()

    assert len(provider_ids) == len(AUDIT_CASES)
    assert len(evaluation_ids) == len(AUDIT_CASES)
    assert len(trace_fingerprints) == len(AUDIT_CASES)
    assert len(response_signatures) == len(AUDIT_CASES)


@pytest.mark.parametrize("case_id", sorted(AUDIT_CASES))
def test_audit_provider_rejects_task_scope_mismatch(case_id: str) -> None:
    task = TaskContract.from_user_input(public_training_case(case_id)["task"])
    identification, identification_id, _, _ = build_training_provider_registries(
        case_id
    )
    provider = identification.get(identification_id)
    protocol = compile_protocol(
        task,
        {"route_id": "test", "experiment_primitives": ["bounded_input_sequence"]},
        provider={
            "provider_id": provider.provider_id,
            "provider_version": provider.provider_version,
            "capabilities": provider.capabilities,
        },
    ).to_dict()
    mismatched_task = TaskContract.from_user_input(
        public_training_case("dc_motor_speed_v1")["task"]
    )

    with pytest.raises(ValueError, match="audit_provider_task_scope_mismatch"):
        provider.execute(protocol, task=mismatched_task.to_dict())


@pytest.mark.parametrize("case_id", sorted(AUDIT_CASES))
def test_audit_cases_run_to_a_valid_kernel_boundary(tmp_path, case_id: str) -> None:
    service = WorkflowService(tmp_path / case_id)
    session = service.start_registered_case(case_id)
    session = service.confirm_task(
        session.session_id, action_id="confirm", revision=session.revision
    )
    session = service.submit_answer(
        session.session_id,
        action_id="diagnostics",
        revision=session.revision,
        answer=_diagnostics(case_id),
    )
    session = service.advance(
        session.session_id, action_id="route", revision=session.revision
    )

    expected = _EXPECTED_ROUTE_FAMILIES[case_id]
    if case_id == "audit_class_iv_high_order":
        # The current generic Class IV policy remains a deliberate capability
        # boundary until public phase evidence resolves an executable route.
        assert session.status == "capability_gap"
    else:
        assert session.route["controller_contract_id"] == expected
        registries = build_training_provider_registries(case_id)
        session = service.run_until_blocked(
            session.session_id,
            provider_registry=registries[0],
            identification_provider_id=registries[1],
            evaluation_provider_registry=registries[2],
            evaluation_provider_id=registries[3],
        )
        assert session.status in {
            "performance_met",
            "tuning_eligible",
            "capability_gap",
            "awaiting_evidence",
        }
        assert all(
            "provider_task_scope_mismatch" not in str(event.payload)
            for event in session.events
        )
