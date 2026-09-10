from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from uuid import uuid4

from cfdc.doctor import run_doctor
from cfdc.kernel import WorkflowService
from cfdc.kernel.cases import public_case_catalog


def parse_safety_bounds(values: list[str]) -> dict[str, float]:
    bounds: dict[str, float] = {}
    for item in values:
        key, separator, raw_value = item.partition("=")
        key = key.strip()
        if not separator or not key or not raw_value.strip():
            raise SystemExit(f"invalid --safety-bound {item!r}; expected KEY=FLOAT")
        if key in bounds:
            raise SystemExit(f"duplicate --safety-bound key '{key}'")
        try:
            value = float(raw_value)
        except ValueError:
            raise SystemExit(
                f"invalid --safety-bound {item!r}; value must be a float"
            ) from None
        if not math.isfinite(value):
            raise SystemExit(f"invalid --safety-bound {item!r}; value must be finite")
        bounds[key] = value
    return bounds


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the CFDC Kernel workflow.", allow_abbrev=False
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Run non-destructive environment checks and print structured JSON.",
    )
    parser.add_argument(
        "--description", type=str, help="Plain-language system description."
    )
    parser.add_argument(
        "--task-type",
        choices=[
            "local_setpoint_hold",
            "transition_then_hold",
            "disturbance_recovery_to_hold",
        ],
        default=None,
        help="Kernel task type; used when creating a custom task.",
    )
    parser.add_argument(
        "--kernel-session-dir",
        type=Path,
        default=None,
        help="Directory for Kernel session JSON files (default: output/kernel-sessions).",
    )
    parser.add_argument(
        "--kernel-session",
        type=str,
        default=None,
        help="Read or advance a Kernel session by ID.",
    )
    parser.add_argument(
        "--kernel-case",
        choices=sorted(public_case_catalog()),
        default=None,
        help="Start or resume with a registered engineering/audit case and its software providers.",
    )
    parser.add_argument(
        "--kernel-evidence-mode",
        choices=["automatic", "exercise_bundle"],
        default="automatic",
        help="Evidence mode for a newly started registered case.",
    )
    parser.add_argument(
        "--kernel-import-result",
        type=Path,
        default=None,
        help="Import a current Kernel result ZIP into a new session.",
    )
    parser.add_argument(
        "--kernel-action",
        type=str,
        default=None,
        help="Stable action ID for a kernel mutation; repeated IDs are idempotent.",
    )
    parser.add_argument(
        "--kernel-answer",
        type=str,
        default=None,
        help="JSON object containing kernel diagnostic answers.",
    )
    parser.add_argument(
        "--kernel-evidence",
        type=Path,
        default=None,
        help="JSON public evidence payload for a kernel session.",
    )
    parser.add_argument(
        "--kernel-phase-result",
        type=Path,
        default=None,
        help="JSON public result for the next frozen multi-stage phase.",
    )
    parser.add_argument(
        "--kernel-features",
        type=Path,
        default=None,
        help="JSON source-bound feature artifact for a kernel session.",
    )
    parser.add_argument(
        "--kernel-controller",
        type=Path,
        default=None,
        help="JSON restricted Controller IR for a kernel session.",
    )
    parser.add_argument(
        "--kernel-evaluation",
        type=Path,
        default=None,
        help="JSON public evaluation packet for a kernel session.",
    )
    parser.add_argument(
        "--kernel-relevance",
        type=Path,
        default=None,
        help="JSON deterministic not_relevant declarations for a kernel session.",
    )
    parser.add_argument(
        "--kernel-provider",
        type=Path,
        default=None,
        help="JSON public provider binding for a kernel session.",
    )
    parser.add_argument(
        "--kernel-compile-protocol",
        action="store_true",
        help="Compile the next versioned experiment protocol.",
    )
    parser.add_argument(
        "--kernel-protocol-request",
        type=Path,
        default=None,
        help="Optional JSON overrides for --kernel-compile-protocol.",
    )
    parser.add_argument(
        "--kernel-prepare-operator-handoff",
        action="store_true",
        help="Write the operator card, templates, schema, checklist, and ZIP bundle.",
    )
    parser.add_argument(
        "--kernel-prepare-training-exercise",
        action="store_true",
        help="Generate a protocol-bound software teaching exercise ZIP without ingesting evidence.",
    )
    parser.add_argument(
        "--kernel-operator-report",
        type=Path,
        default=None,
        help="JSON operator decision and completed prechecks.",
    )
    parser.add_argument(
        "--kernel-upload",
        type=Path,
        action="append",
        default=[],
        help="Protocol-bound CSV or JSON experiment data; can be repeated.",
    )
    parser.add_argument(
        "--kernel-upload-stopped-on-limit",
        action="store_true",
        help="Record that the uploaded experiment stopped on a declared limit.",
    )
    parser.add_argument(
        "--kernel-run-provider",
        action="store_true",
        help="Run the registered identification provider for the active protocol.",
    )
    parser.add_argument(
        "--kernel-derive-features",
        action="store_true",
        help="Derive a source-bound FeatureArtifact from accepted public evidence.",
    )
    parser.add_argument(
        "--kernel-synthesize-controller",
        action="store_true",
        help="Run deterministic controller synthesis for the resolved route.",
    )
    parser.add_argument(
        "--kernel-qualify-controller",
        action="store_true",
        help="Run the route-specific offline controller qualification.",
    )
    parser.add_argument(
        "--kernel-run-evaluation",
        action="store_true",
        help="Run the independently bound evaluation provider.",
    )
    parser.add_argument(
        "--kernel-run-feedback",
        action="store_true",
        help="Run one bounded feedback iteration when performance is insufficient.",
    )
    parser.add_argument(
        "--kernel-confirm-result",
        action="store_true",
        help="Run the mandatory fresh confirmation for an accepted tuned freeze.",
    )
    parser.add_argument(
        "--kernel-auto",
        action="store_true",
        help="Advance deterministic Kernel steps until human input, external data, confirmation, or a terminal state is required.",
    )
    parser.add_argument(
        "--kernel-result-dir",
        type=Path,
        default=None,
        help="Write the public result/audit ZIP to this directory.",
    )
    parser.add_argument(
        "--kernel-export-bundle",
        action="store_true",
        help="Export the public result and full audit ZIP after the requested actions.",
    )
    parser.add_argument(
        "--confirm-kernel-budget",
        action="store_true",
        help="Confirm the kernel task's software experiment budget before mutation.",
    )
    parser.add_argument(
        "--kernel-advance",
        action="store_true",
        help="Run deterministic diagnostic route resolution for a kernel session.",
    )
    parser.add_argument(
        "--kernel-freeze",
        action="store_true",
        help="Freeze a submitted kernel controller candidate using default software contracts.",
    )
    parser.add_argument(
        "--kernel-replay",
        action="store_true",
        help="Replay the latest stored public evaluation packet without running a provider.",
    )
    parser.add_argument(
        "--kernel-tuning",
        type=Path,
        default=None,
        help="JSON bounded tuning contract for a kernel session.",
    )
    parser.add_argument(
        "--kernel-tuning-results",
        type=Path,
        default=None,
        help="JSON precomputed public tuning results keyed by split and parameters.",
    )
    parser.add_argument(
        "--kernel-confirmation",
        type=Path,
        default=None,
        help="JSON fresh confirmation packet for an accepted tuning result.",
    )
    parser.add_argument(
        "--observed-output",
        action="append",
        default=[],
        help="Measured output name. Can be repeated.",
    )
    parser.add_argument(
        "--actuator",
        action="append",
        default=[],
        help="Actuator or input name. Can be repeated.",
    )
    parser.add_argument(
        "--safety-bound",
        action="append",
        default=[],
        metavar="KEY=FLOAT",
        help="Safety bound. Can be repeated.",
    )
    parser.add_argument(
        "--rag-index",
        type=Path,
        default=None,
        help="Local RAG index directory created by `python -m cfdc.rag index`.",
    )
    parser.add_argument(
        "--rag-snapshot",
        type=str,
        default=None,
        help="Pin one validated local RAG snapshot instead of CURRENT.",
    )
    parser.add_argument(
        "--no-rag",
        action="store_true",
        help="Disable local RAG for this run without changing the index.",
    )
    parser.add_argument(
        "--llm-base-url",
        type=str,
        default=None,
        help="Provider API root, e.g. https://api.deepseek.com or http://localhost:11434/v1 (env: CFDC_LLM_BASE_URL).",
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default=None,
        help="Provider model identifier (env: CFDC_LLM_MODEL).",
    )
    parser.add_argument(
        "--llm-api-key",
        type=str,
        default=None,
        help="Provider API key (env: CFDC_LLM_API_KEY). Prefer environment variables for normal use.",
    )
    return parser.parse_args(argv)


def _read_kernel_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid {label} JSON: {exc}") from None
    if not isinstance(value, dict):
        raise SystemExit(f"{label} JSON must contain an object")
    return value


def _training_context(case_id: str | None):
    if not case_id:
        return None
    from cfdc.sim.training import build_training_provider_registries

    return build_training_provider_registries(case_id)


def _bind_training_providers(
    service: WorkflowService,
    session,
    *,
    action_id: str,
    context,
):
    identification_registry, identification_id, evaluation_registry, evaluation_id = (
        context
    )
    for role, registry, provider_id in (
        ("identification", identification_registry, identification_id),
        ("evaluation", evaluation_registry, evaluation_id),
    ):
        provider = registry.get(provider_id)
        existing = session.provider_bindings.get(role)
        if isinstance(existing, dict):
            if existing.get("provider_id") != provider_id:
                raise SystemExit(
                    f"registered {role} provider does not match --kernel-case"
                )
            continue
        session = service.set_provider(
            session.session_id,
            action_id=f"{action_id}:bind-{role}",
            revision=session.revision,
            provider={
                "provider_id": provider.provider_id,
                "provider_version": provider.provider_version,
                "capabilities": sorted(str(item) for item in provider.capabilities),
                "binding_role": role,
                "execution_kind": "software",
            },
        )
    return session


def _run_kernel_cli(args: argparse.Namespace, safety_bounds: dict[str, float]) -> None:
    service = WorkflowService(
        args.kernel_session_dir or Path("output") / "kernel-sessions"
    )
    action_id = args.kernel_action or f"cli-{uuid4().hex}"
    if args.kernel_import_result is not None:
        if args.kernel_session:
            raise SystemExit(
                "--kernel-import-result cannot be combined with --kernel-session"
            )
        session = service.import_result_bundle(args.kernel_import_result)
    elif args.kernel_session:
        session = service.read(args.kernel_session)
    else:
        if not args.kernel_case:
            if not args.description:
                raise SystemExit(
                    "A new Kernel task requires --description or --kernel-case for a new task"
                )
            payload = {
                "description": args.description,
                "task_type": args.task_type or "local_setpoint_hold",
                "measured_signals": args.observed_output or ["output"],
                "control_input": (args.actuator[0] if args.actuator else "input"),
                "control_inputs": args.actuator or ["input"],
                "input_min": safety_bounds.get("input_min"),
                "input_max": safety_bounds.get("input_max"),
                "output_min": safety_bounds.get("output_min"),
                "output_max": safety_bounds.get("output_max"),
                "state_stop": safety_bounds.get("state_stop"),
                "signal_units": {},
                "workspace": {"source": "cli"},
            }
            payload = {
                key: value for key, value in payload.items() if value is not None
            }
        rag_snapshot = args.rag_snapshot
        rag_requested = not args.no_rag
        if rag_requested and args.rag_index is not None:
            from cfdc.rag import load_index

            index = load_index(
                args.rag_index,
                snapshot_name=args.rag_snapshot,
                load_encoder=False,
            )
            rag_snapshot = index.index_snapshot
        elif rag_requested and rag_snapshot:
            raise SystemExit("--rag-snapshot requires --rag-index for a kernel task")
        rag_active = bool(rag_requested and rag_snapshot)
        agent_config = {
            "mode": "multi",
            "rag_requested": rag_requested,
            "rag_enabled": rag_active,
            "rag_status": (
                "active"
                if rag_active
                else "not_initialized"
                if rag_requested
                else "disabled"
            ),
            "rag_index_dir": str(args.rag_index)
            if args.rag_index is not None
            else None,
            "llm_configured": False,
        }
        session = (
            service.start_registered_case(
                args.kernel_case,
                agent_config=agent_config,
                rag_snapshot=rag_snapshot,
                evidence_mode=args.kernel_evidence_mode,
            )
            if args.kernel_case
            else service.start(
                payload,
                agent_config=agent_config,
                rag_snapshot=rag_snapshot,
            )
        )
    if args.confirm_kernel_budget:
        session = service.confirm_task(
            session.session_id,
            action_id=f"{action_id}:confirm",
            revision=session.revision,
        )
    if args.kernel_answer is not None:
        try:
            answer = json.loads(args.kernel_answer)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid --kernel-answer JSON: {exc}") from None
        if not isinstance(answer, dict):
            raise SystemExit("--kernel-answer must be a JSON object")
        session = service.submit_answer(
            session.session_id,
            action_id=f"{action_id}:answer",
            revision=session.revision,
            answer=answer,
        )
    if args.kernel_relevance is not None:
        declarations = _read_kernel_json(args.kernel_relevance, "kernel relevance")
        session = service.apply_task_relevance(
            session.session_id,
            action_id=f"{action_id}:relevance",
            revision=session.revision,
            declarations={str(key): str(value) for key, value in declarations.items()},
        )
    if args.kernel_advance:
        session = service.advance(
            session.session_id,
            action_id=f"{action_id}:advance",
            revision=session.revision,
        )
    if args.kernel_evidence is not None:
        evidence = _read_kernel_json(args.kernel_evidence, "kernel evidence")
        session = service.submit_evidence(
            session.session_id,
            action_id=f"{action_id}:evidence",
            revision=session.revision,
            evidence=evidence,
        )
    if args.kernel_phase_result is not None:
        phase_result = _read_kernel_json(
            args.kernel_phase_result, "kernel phase result"
        )
        session = service.record_phase_result(
            session.session_id,
            action_id=f"{action_id}:phase",
            revision=session.revision,
            result=phase_result,
        )
    if args.kernel_features is not None:
        features = _read_kernel_json(args.kernel_features, "kernel features")
        quality = features.pop("quality", None)
        payload = features.get("features", features)
        session = service.submit_features(
            session.session_id,
            action_id=f"{action_id}:features",
            revision=session.revision,
            features=payload,
            quality=quality,
        )
    if args.kernel_controller is not None:
        controller = _read_kernel_json(args.kernel_controller, "kernel controller")
        session = service.submit_controller(
            session.session_id,
            action_id=f"{action_id}:controller",
            revision=session.revision,
            controller=controller,
        )
    if args.kernel_provider is not None:
        provider = _read_kernel_json(args.kernel_provider, "kernel provider")
        session = service.set_provider(
            session.session_id,
            action_id=f"{action_id}:provider",
            revision=session.revision,
            provider=provider,
        )
    registered = session.registered_case_binding
    configured_case_id = (
        str(registered.get("case_id") or "") if isinstance(registered, dict) else ""
    )
    if (
        args.kernel_case
        and configured_case_id
        and args.kernel_case != configured_case_id
    ):
        raise SystemExit("--kernel-case does not match the registered session case")
    training_context = _training_context(configured_case_id)
    provider_actions_requested = any(
        (
            args.kernel_auto,
            args.kernel_compile_protocol,
            args.kernel_run_provider,
            args.kernel_run_evaluation,
            args.kernel_run_feedback,
            args.kernel_confirm_result,
        )
    )
    if (
        training_context is not None
        and provider_actions_requested
        and session.registered_case_binding is None
    ):
        session = _bind_training_providers(
            service,
            session,
            action_id=action_id,
            context=training_context,
        )
    if args.kernel_compile_protocol:
        request = (
            _read_kernel_json(args.kernel_protocol_request, "kernel protocol request")
            if args.kernel_protocol_request is not None
            else None
        )
        session = service.compile_protocol(
            session.session_id,
            action_id=f"{action_id}:protocol",
            revision=session.revision,
            request=request,
        )
    elif args.kernel_protocol_request is not None:
        raise SystemExit("--kernel-protocol-request requires --kernel-compile-protocol")
    if args.kernel_prepare_operator_handoff:
        output_dir = (
            args.kernel_result_dir / f"{session.session_id}.operator"
            if args.kernel_result_dir is not None
            else None
        )
        session = service.prepare_operator_handoff(
            session.session_id,
            action_id=f"{action_id}:operator-handoff",
            revision=session.revision,
            output_dir=output_dir,
        )
    if args.kernel_prepare_training_exercise:
        if training_context is None:
            raise SystemExit(
                "--kernel-prepare-training-exercise requires --kernel-case"
            )
        identification_registry, identification_id, _, _ = training_context
        output_dir = (
            args.kernel_result_dir / f"{session.session_id}.exercise"
            if args.kernel_result_dir is not None
            else None
        )
        session = service.prepare_training_exercise_bundle(
            session.session_id,
            action_id=f"{action_id}:training-exercise",
            revision=session.revision,
            provider_registry=identification_registry,
            provider_id=identification_id,
            output_dir=output_dir,
        )
    if args.kernel_operator_report is not None:
        report = _read_kernel_json(
            args.kernel_operator_report, "kernel operator report"
        )
        session = service.record_operator_report(
            session.session_id,
            action_id=f"{action_id}:operator-report",
            revision=session.revision,
            report=report,
        )
    if args.kernel_upload:
        session = service.ingest_upload(
            session.session_id,
            action_id=f"{action_id}:upload",
            revision=session.revision,
            paths=args.kernel_upload,
            stopped_on_limit=args.kernel_upload_stopped_on_limit,
        )
    if args.kernel_run_provider:
        if training_context is None:
            raise SystemExit("--kernel-run-provider requires --kernel-case")
        identification_registry, identification_id, _, _ = training_context
        session = service.run_provider(
            session.session_id,
            action_id=f"{action_id}:provider-run",
            revision=session.revision,
            provider_registry=identification_registry,
            provider_id=identification_id,
        )
    if args.kernel_derive_features:
        session = service.derive_features(
            session.session_id,
            action_id=f"{action_id}:derive-features",
            revision=session.revision,
        )
    if args.kernel_synthesize_controller:
        session = service.synthesize_controller(
            session.session_id,
            action_id=f"{action_id}:synthesize-controller",
            revision=session.revision,
        )
    if args.kernel_qualify_controller:
        session = service.qualify_controller(
            session.session_id,
            action_id=f"{action_id}:qualify-controller",
            revision=session.revision,
        )
    if args.kernel_freeze:
        if not session.controller_candidate:
            raise SystemExit(
                "--kernel-freeze requires a submitted --kernel-controller candidate"
            )
        controller = session.controller_candidate.get("ir", {})
        session = service.freeze_controller(
            session.session_id,
            action_id=f"{action_id}:freeze",
            revision=session.revision,
            controller=controller,
            runtime_contract={
                "software_only": True,
                "command_bounds": [
                    safety_bounds.get("input_min", -1.0),
                    safety_bounds.get("input_max", 1.0),
                ],
            },
            evaluation_contract={"criteria": "public_stability_then_performance"},
        )
    if args.kernel_run_evaluation:
        if training_context is None:
            raise SystemExit("--kernel-run-evaluation requires --kernel-case")
        _, _, evaluation_registry, evaluation_id = training_context
        session = service.run_evaluation(
            session.session_id,
            action_id=f"{action_id}:provider-evaluation",
            revision=session.revision,
            provider_registry=evaluation_registry,
            provider_id=evaluation_id,
        )
    if args.kernel_evaluation is not None:
        packet = _read_kernel_json(args.kernel_evaluation, "kernel evaluation")
        session = service.record_evaluation(
            session.session_id,
            action_id=f"{action_id}:evaluation",
            revision=session.revision,
            packet=packet,
        )
    if args.kernel_replay:
        session = service.replay_evaluation(
            session.session_id,
            action_id=f"{action_id}:replay",
            revision=session.revision,
        )
    if args.kernel_tuning is not None:
        contract = _read_kernel_json(args.kernel_tuning, "kernel tuning contract")
        if args.kernel_tuning_results is None:
            raise SystemExit("--kernel-tuning requires --kernel-tuning-results")
        try:
            results_value = json.loads(
                args.kernel_tuning_results.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise SystemExit(f"invalid kernel tuning results JSON: {exc}") from None
        result_rows = (
            results_value.get("results", results_value)
            if isinstance(results_value, dict)
            else results_value
        )
        if not isinstance(result_rows, list) or not all(
            isinstance(item, dict) for item in result_rows
        ):
            raise SystemExit("kernel tuning results must be a JSON list of objects")

        def evaluate(parameters, split, repeats):
            for row in result_rows:
                if (
                    str(row.get("split")) == split
                    and int(row.get("repeats", repeats)) == repeats
                    and row.get("parameters") == dict(parameters)
                ):
                    value = row.get("result", row)
                    if isinstance(value, dict):
                        return dict(value)
            return {
                "hard_failure": True,
                "stable": False,
                "reason": "missing_precomputed_tuning_result",
            }

        session = service.run_tuning(
            session.session_id,
            action_id=f"{action_id}:tuning",
            revision=session.revision,
            contract=contract,
            evaluate=evaluate,
        )
    if args.kernel_confirmation is not None:
        packet = _read_kernel_json(args.kernel_confirmation, "kernel confirmation")
        session = service.record_confirmation(
            session.session_id,
            action_id=f"{action_id}:confirmation",
            revision=session.revision,
            packet=packet,
        )
    if args.kernel_run_feedback:
        if training_context is None:
            raise SystemExit("--kernel-run-feedback requires --kernel-case")
        _, _, evaluation_registry, evaluation_id = training_context
        session = service.run_feedback_iteration(
            session.session_id,
            action_id=f"{action_id}:feedback",
            revision=session.revision,
            provider_registry=evaluation_registry,
            provider_id=evaluation_id,
        )
    if args.kernel_confirm_result:
        if training_context is None:
            raise SystemExit("--kernel-confirm-result requires --kernel-case")
        _, _, evaluation_registry, evaluation_id = training_context
        session = service.confirm_result(
            session.session_id,
            action_id=f"{action_id}:confirm-result",
            revision=session.revision,
            provider_registry=evaluation_registry,
            provider_id=evaluation_id,
        )
    if args.kernel_auto:
        if training_context is None:
            session = service.run_until_blocked(session.session_id)
        else:
            (
                identification_registry,
                identification_id,
                evaluation_registry,
                evaluation_id,
            ) = training_context
            session = service.run_until_blocked(
                session.session_id,
                provider_registry=identification_registry,
                identification_provider_id=identification_id,
                evaluation_provider_registry=evaluation_registry,
                evaluation_provider_id=evaluation_id,
            )
    bundle_path = None
    if args.kernel_export_bundle or args.kernel_result_dir is not None:
        output = (
            args.kernel_result_dir / f"{session.session_id}.result.zip"
            if args.kernel_result_dir is not None
            else None
        )
        bundle_path = service.export_result_bundle(session.session_id, output)
    result = session.to_dict()
    if bundle_path is not None:
        result["result_bundle_path"] = str(bundle_path)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> None:
    args = parse_args()
    safety_bounds = parse_safety_bounds(args.safety_bound)
    if args.doctor:
        report = run_doctor(
            session_dir=args.kernel_session_dir,
            rag_index_dir=args.rag_index,
            ollama_base_url=args.llm_base_url,
            ollama_model=args.llm_model,
            api_key=args.llm_api_key,
        )
        payload = report.to_dict()
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        if not bool(payload.get("ok")):
            raise SystemExit(1)
        return
    _run_kernel_cli(args, safety_bounds)


if __name__ == "__main__":
    main()
