from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from uuid import uuid4

from cfdc.agents import wrap_agent_adapter
from cfdc.demo import run_demo_validation
from cfdc.diagnosis import (
    OpenAICompatibleDiagnosticAdapter,
    migrate_diagnostic_session_payload,
    run_diagnostic_evaluation,
    run_live_llm_diagnostic_comparison,
    run_saved_llm_diagnostic_comparison,
    start_diagnostic_session,
    validate_guided_adapter_capabilities,
)
from cfdc.doctor import run_doctor
from cfdc.evidence import plant_id_for_description
from cfdc.kernel import WorkflowService
from cfdc.kernel.cases import public_case_catalog
from cfdc.models import (
    CFDCRunReport,
    ClosedLoopValidationSpec,
    DiagnosticSessionState,
    MeasuredTraceManifest,
    PlantEvidencePackage,
    SystemDescription,
)
from cfdc.runtime import run_cfdc_route
from cfdc.sim import (
    run_benchmark_suite,
    run_feature_ablation_suite,
    run_vtol_simulation,
    simulate_cartpole_energy_swingup,
)


def compact_route_report(report: CFDCRunReport) -> dict:
    payload = report.model_dump()
    for result in payload.get("experiment_results", []):
        trace = result.get("trace")
        if trace:
            trace["sample_count"] = len(trace.get("time_s", []))
            trace["signal_names"] = sorted(trace.get("signals", {}))
            trace.pop("time_s", None)
            trace.pop("signals", None)
    for trial in payload.get("trial_reports", []):
        samples = trial.pop("samples", [])
        trial["sample_count"] = len(samples)
    boundary = payload.get("cartpole_boundary")
    if boundary:
        nested_trials = list(boundary.get("candidate_trials", []))
        rollback_trial = boundary.get("rollback_trial")
        if rollback_trial:
            nested_trials.append(rollback_trial)
        for trial in nested_trials:
            samples = trial.pop("samples", [])
            trial["sample_count"] = len(samples)
    search_state = payload.get("safe_gain_search_state")
    if search_state:
        history = search_state.pop("history", [])
        search_state["history_count"] = len(history)
        search_state["history_tail"] = history[-5:]
    cartpole_simulation = payload.get("cartpole_simulation")
    if cartpole_simulation:
        events = cartpole_simulation.pop("events", [])
        cartpole_simulation["event_count"] = len(events)
        cartpole_simulation["event_tail"] = events[-5:]
    return payload


def _positive_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0.0:
        raise argparse.ArgumentTypeError("must be a finite number greater than zero")
    return parsed


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


def load_diagnostic_session(path: Path) -> DiagnosticSessionState:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return migrate_diagnostic_session_payload(payload)
    except (OSError, TypeError, ValueError) as exc:
        raise SystemExit(f"invalid --diagnostic-session-input {path}: {exc}") from None


def write_diagnostic_session_atomic(
    path: Path,
    session: DiagnosticSessionState,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(session.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def parse_diagnostic_answers(values: list[str]) -> dict[str, str]:
    answers: dict[str, str] = {}
    for item in values:
        question, separator, answer = item.partition("=")
        if not separator or not question.strip() or not answer.strip():
            raise SystemExit(
                f"invalid --diagnostic-answer {item!r}; expected QUESTION_ID=ANSWER"
            )
        if question in answers:
            raise SystemExit(f"duplicate --diagnostic-answer question {question!r}")
        answers[question] = answer
    return answers


def _uses_builtin_experiment_inputs(args: argparse.Namespace) -> bool:
    return bool(
        args.benchmark
        or args.feature_ablation
        or args.diagnostic_eval
        or args.diagnostic_eval_current
        or args.diagnostic_eval_llm
        or args.diagnostic_eval_llm_saved
        or args.validate_demo
        or args.cartpole_swingup
        or args.vtol_sim
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the independent CFDC framework.")
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Run non-destructive environment checks and print structured JSON.",
    )
    parser.add_argument(
        "--description", type=str, help="Plain-language system description."
    )
    parser.add_argument(
        "--workflow-version",
        choices=["legacy", "kernel"],
        default="legacy",
        help="Use the migrated evidence-driven kernel for new tasks (default: legacy compatibility path).",
    )
    parser.add_argument(
        "--task-type",
        choices=[
            "local_setpoint_hold",
            "transition_then_hold",
            "disturbance_recovery_to_hold",
        ],
        default=None,
        help="Kernel task type; selecting it automatically uses the migrated workflow.",
    )
    parser.add_argument(
        "--kernel-session-dir",
        type=Path,
        default=None,
        help="Directory for migrated kernel session JSON files (default: output/kernel-sessions).",
    )
    parser.add_argument(
        "--kernel-session",
        type=str,
        default=None,
        help="Read or advance a migrated kernel session by ID.",
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
        "--kernel-import-v3",
        type=Path,
        default=None,
        help="Read-only import a CFDC v3 directory or ZIP into a new Kernel session.",
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
        "--time-scale-hint-s",
        type=_positive_float,
        default=None,
        help="Positive process time-scale hint in seconds.",
    )
    parser.add_argument(
        "--diagnostic-session-input",
        type=Path,
        default=None,
        help="Resume a DiagnosticSessionState JSON file.",
    )
    parser.add_argument(
        "--diagnostic-session-output",
        type=Path,
        default=None,
        help="Atomically write the resulting DiagnosticSessionState JSON file.",
    )
    parser.add_argument(
        "--diagnostic-answer",
        action="append",
        default=[],
        metavar="QUESTION_ID=ANSWER",
        help="Answer a pending question by stable question ID.",
    )
    parser.add_argument(
        "--diagnostic-description",
        type=str,
        default=None,
        help="Add a free-form supplemental description when resuming a diagnostic session.",
    )
    measurement_group = parser.add_mutually_exclusive_group()
    measurement_group.add_argument(
        "--measurement-response",
        type=str,
        default=None,
        help="Submit existing-record evidence or requested profile facts.",
    )
    measurement_group.add_argument(
        "--measurement-response-file",
        type=Path,
        default=None,
        help="Read the measurement response from a UTF-8 text file.",
    )
    parser.add_argument(
        "--confirm-simulation-bounds",
        action="store_true",
        help=(
            "Confirm that supplied ranges are software-simulation run/stop bounds, "
            "not real-hardware safety certification."
        ),
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run the built-in CFDC synthetic benchmark chain.",
    )
    parser.add_argument(
        "--feature-ablation",
        action="store_true",
        help="Run minimal/noisy/full-model feature ablations.",
    )
    parser.add_argument(
        "--diagnostic-eval",
        action="store_true",
        help="Score the saved 8+4 offline diagnostic responses.",
    )
    parser.add_argument(
        "--diagnostic-eval-current",
        action="store_true",
        help="Score fresh deterministic diagnostic responses.",
    )
    parser.add_argument(
        "--diagnostic-eval-llm",
        action="store_true",
        help="Call the configured LLM for all frozen 8+4 cases, save structured responses, and compare with deterministic results.",
    )
    parser.add_argument(
        "--diagnostic-eval-llm-saved",
        action="store_true",
        help="Compare a previously saved LLM response snapshot with the deterministic baseline.",
    )
    parser.add_argument(
        "--diagnostic-llm-output",
        type=Path,
        default=None,
        help="Optional path for the structured LLM diagnostic response snapshot.",
    )
    parser.add_argument(
        "--validate-demo",
        action="store_true",
        help="Validate the stable Cartpole and VTOL software demo routes.",
    )
    parser.add_argument(
        "--cartpole-swingup",
        action="store_true",
        help="Run the deterministic cartpole energy swing-up simulation.",
    )
    parser.add_argument(
        "--vtol-sim",
        action="store_true",
        help="Run the deterministic planar VTOL simulation.",
    )
    parser.add_argument(
        "--vtol-mode",
        choices=["altitude", "hover", "position", "boundary"],
        default="position",
        help="Planar VTOL simulation mode.",
    )
    parser.add_argument(
        "--run-route",
        choices=[
            "generic",
            "cartpole",
            "cartpole-boundary",
            "vtol-position",
            "vtol-boundary",
            "vtol-altitude",
            "vtol-hover",
            "vtol-variation",
        ],
        help="Run an end-to-end structured CFDC route report.",
    )
    parser.add_argument(
        "--include-trajectory",
        action="store_true",
        help="Include route simulation trajectories in JSON output.",
    )
    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Include raw experiment traces and trial samples in route JSON output.",
    )
    parser.add_argument(
        "--model-spec",
        type=Path,
        default=None,
        help="JSON file containing a structured transfer-function, state-space, or registered nonlinear model.",
    )
    parser.add_argument(
        "--specification-text",
        type=str,
        default=None,
        help="Plain-language equipment specifications or a pasted manual excerpt.",
    )
    parser.add_argument(
        "--specification-answer",
        action="append",
        default=[],
        help="Additional plain-language specification answer; can be repeated.",
    )
    parser.add_argument(
        "--trace-manifest",
        type=Path,
        default=None,
        help="JSON file containing one or more measured CSV trace manifests.",
    )
    parser.add_argument(
        "--validation-spec",
        type=Path,
        default=None,
        help="JSON file containing explicit closed-loop validation references, limits, and performance targets.",
    )
    parser.add_argument(
        "--demo-fixture",
        action="store_true",
        help="Explicitly run the selected standard profile as a demo fixture; results do not represent the user object.",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use the configured OpenAI-compatible provider for role-scoped agent work; routing remains deterministic.",
    )
    parser.add_argument(
        "--agent-mode",
        choices=["single", "multi"],
        default=None,
        help="Agent orchestration mode (default: multi; CFDC_AGENT_MODE can override).",
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
        "--use-mechanism-cards",
        action="store_true",
        help="Add optional mechanism-card labels without changing the canonical archetype route.",
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
    parser.add_argument(
        "--llm-timeout-s",
        type=float,
        default=60.0,
        help="LLM request timeout in seconds.",
    )
    parser.add_argument(
        "--llm-max-tokens",
        type=int,
        default=1400,
        help="Maximum diagnostic response tokens.",
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
    if args.kernel_import_v3 is not None:
        if args.kernel_session:
            raise SystemExit(
                "--kernel-import-v3 cannot be combined with --kernel-session"
            )
        session = service.import_v3(args.kernel_import_v3)
    elif args.kernel_session:
        session = service.read(args.kernel_session)
    else:
        if not args.kernel_case:
            if not args.description:
                raise SystemExit(
                    "--workflow-version kernel requires --description or --kernel-case for a new task"
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
            "mode": args.agent_mode or "multi",
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
            "llm_configured": bool(args.use_llm),
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
    if (
        args.workflow_version == "kernel"
        or args.task_type is not None
        or args.kernel_session is not None
        or args.kernel_case is not None
        or args.kernel_import_v3 is not None
        or args.kernel_answer is not None
        or args.kernel_evidence is not None
        or args.kernel_phase_result is not None
        or args.kernel_features is not None
        or args.kernel_controller is not None
        or args.kernel_evaluation is not None
        or args.kernel_relevance is not None
        or args.kernel_provider is not None
        or args.kernel_compile_protocol
        or args.kernel_protocol_request is not None
        or args.kernel_prepare_operator_handoff
        or args.kernel_prepare_training_exercise
        or args.kernel_operator_report is not None
        or bool(args.kernel_upload)
        or args.kernel_upload_stopped_on_limit
        or args.kernel_run_provider
        or args.kernel_derive_features
        or args.kernel_synthesize_controller
        or args.kernel_qualify_controller
        or args.kernel_run_evaluation
        or args.kernel_run_feedback
        or args.kernel_confirm_result
        or args.kernel_auto
        or args.kernel_result_dir is not None
        or args.kernel_export_bundle
        or args.kernel_advance
        or args.kernel_freeze
        or args.kernel_replay
        or args.kernel_tuning is not None
        or args.kernel_tuning_results is not None
        or args.kernel_confirmation is not None
        or args.confirm_kernel_budget
    ):
        _run_kernel_cli(args, safety_bounds)
        return
    session_state = (
        load_diagnostic_session(args.diagnostic_session_input)
        if args.diagnostic_session_input is not None
        else None
    )
    diagnostic_answers = parse_diagnostic_answers(args.diagnostic_answer)
    if diagnostic_answers and session_state is None:
        raise SystemExit("--diagnostic-answer requires --diagnostic-session-input")
    if (
        args.measurement_response is not None
        or args.measurement_response_file is not None
    ) and session_state is None:
        raise SystemExit("--measurement-response requires --diagnostic-session-input")
    adapter = None
    if args.use_llm or args.diagnostic_eval_llm:
        try:
            base_adapter = OpenAICompatibleDiagnosticAdapter(
                base_url=args.llm_base_url,
                model=args.llm_model,
                api_key=args.llm_api_key,
                timeout_s=args.llm_timeout_s,
                max_tokens=args.llm_max_tokens,
            )
            if args.use_llm and not args.diagnostic_eval_llm:
                adapter = wrap_agent_adapter(
                    base_adapter,
                    agent_mode=args.agent_mode,
                    rag_index_dir=(
                        str(args.rag_index) if args.rag_index is not None else None
                    ),
                    rag_snapshot=args.rag_snapshot,
                    use_rag=not args.no_rag,
                )
            else:
                # Frozen LLM evaluations intentionally measure the underlying
                # adapter and must not add the runtime critic to the baseline.
                adapter = base_adapter
        except ValueError as exc:
            raise SystemExit(str(exc)) from None

    if args.validate_demo:
        result = run_demo_validation()
        print(json.dumps(result, indent=2, sort_keys=True))
        if not result["passed"]:
            raise SystemExit(1)
        return
    if args.benchmark:
        print(json.dumps(run_benchmark_suite(), indent=2, sort_keys=True))
        return
    if args.feature_ablation:
        print(
            json.dumps(
                run_feature_ablation_suite().model_dump(mode="json"),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.diagnostic_eval or args.diagnostic_eval_current:
        result = run_diagnostic_evaluation(
            use_saved_responses=not args.diagnostic_eval_current,
        )
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
        return
    if args.diagnostic_eval_llm:
        if adapter is None:
            raise RuntimeError(
                "LLM diagnostic evaluation requires a configured adapter"
            )
        kwargs = {}
        if args.diagnostic_llm_output is not None:
            kwargs["output_path"] = args.diagnostic_llm_output
        result = run_live_llm_diagnostic_comparison(adapter, **kwargs)
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
        return
    if args.diagnostic_eval_llm_saved:
        kwargs = {}
        if args.diagnostic_llm_output is not None:
            kwargs["path"] = args.diagnostic_llm_output
        result = run_saved_llm_diagnostic_comparison(**kwargs)
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
        return
    if args.cartpole_swingup:
        print(
            json.dumps(
                simulate_cartpole_energy_swingup(include_trajectory=False).model_dump(),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.vtol_sim:
        print(
            json.dumps(
                run_vtol_simulation(
                    mode=args.vtol_mode, include_trajectory=args.include_trajectory
                ).model_dump(),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.run_route or session_state is not None or args.description:
        description = None
        if args.description:
            description = SystemDescription(
                text=args.description,
                observed_outputs=args.observed_output,
                actuators=args.actuator,
                safety_bounds=safety_bounds,
                time_scale_hint_s=args.time_scale_hint_s,
            )
        route_id = args.run_route or (
            session_state.route_id if session_state is not None else "generic"
        )
        if route_id == "generic" and adapter is None:
            raise SystemExit(
                "The generic guided measurement flow requires an LLM; use --use-llm."
            )
        if route_id == "generic":
            try:
                validate_guided_adapter_capabilities(adapter)
            except ValueError as exc:
                raise SystemExit(str(exc)) from None
        try:
            measurement_response = (
                args.measurement_response_file.read_text(encoding="utf-8")
                if args.measurement_response_file is not None
                else args.measurement_response
            )
        except (OSError, UnicodeError) as exc:
            raise SystemExit(
                f"invalid --measurement-response-file {args.measurement_response_file}: {exc}"
            ) from None
        if measurement_response is not None and not measurement_response.strip():
            source = (
                "--measurement-response-file"
                if args.measurement_response_file is not None
                else "--measurement-response"
            )
            raise SystemExit(f"{source} must contain non-empty UTF-8 text")
        specification_parts = [
            item.strip()
            for item in [args.specification_text, *args.specification_answer]
            if item and item.strip()
        ]
        specification_text = "\n".join(specification_parts) or None
        if specification_text is not None and (
            session_state is not None or route_id == "generic"
        ):
            raise SystemExit(
                "v4 guided sessions require --measurement-response; "
                "--specification-text is unsupported"
            )
        if measurement_response is not None and (
            diagnostic_answers
            or args.diagnostic_description is not None
            or specification_text is not None
        ):
            raise SystemExit(
                "--measurement-response cannot be combined with diagnostic answers, "
                "--diagnostic-description, or --specification-text"
            )
        if args.validation_spec is not None and args.model_spec is None:
            raise SystemExit("--validation-spec requires --model-spec")
        if specification_text is not None and (
            args.model_spec is not None or args.trace_manifest is not None
        ):
            raise SystemExit(
                "plain-language specifications cannot be combined with structured model or trace evidence"
            )
        if args.demo_fixture and (
            args.model_spec is not None
            or args.trace_manifest is not None
            or specification_text is not None
        ):
            raise SystemExit(
                "--demo-fixture cannot be combined with user-object model or trace evidence"
            )
        evidence_package = None
        if args.model_spec is not None or args.trace_manifest is not None:
            evidence_description = (
                description
                if description is not None
                else session_state.accumulated_description
                if session_state is not None
                else None
            )
            if evidence_description is None:
                raise SystemExit(
                    "object evidence requires --description or --diagnostic-session-input"
                )
            try:
                model_payload = (
                    json.loads(args.model_spec.read_text(encoding="utf-8"))
                    if args.model_spec is not None
                    else None
                )
                trace_payload = (
                    json.loads(args.trace_manifest.read_text(encoding="utf-8"))
                    if args.trace_manifest is not None
                    else []
                )
                if isinstance(trace_payload, dict):
                    trace_payload = trace_payload.get("measured_traces", [])
                manifests = []
                for item in trace_payload:
                    resolved = dict(item)
                    csv_path = Path(resolved["csv_path"])
                    if not csv_path.is_absolute() and args.trace_manifest is not None:
                        resolved["csv_path"] = str(
                            args.trace_manifest.parent / csv_path
                        )
                    manifests.append(MeasuredTraceManifest.model_validate(resolved))
                validation = (
                    ClosedLoopValidationSpec.model_validate_json(
                        args.validation_spec.read_text(encoding="utf-8")
                    )
                    if args.validation_spec is not None
                    else None
                )
                evidence_package = PlantEvidencePackage.model_validate(
                    {
                        "plant_id": plant_id_for_description(evidence_description),
                        "model": model_payload,
                        "measured_traces": manifests,
                        "validation_spec": validation,
                        "provenance": ["CLI structured object evidence"],
                    }
                )
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise SystemExit(f"invalid object evidence: {exc}") from None
        if session_state is not None and route_id != session_state.route_id:
            raise SystemExit("--run-route must match the diagnostic session route_id")
        if session_state is None and args.diagnostic_session_output is not None:
            if description is None:
                description = SystemDescription(
                    text=(
                        "A route description was not supplied; ask for the missing "
                        "system behavior, sensors, actuators, and safety bounds."
                    )
                )
            session_state = start_diagnostic_session(
                description,
                route_id=route_id,
                diagnostic_adapter=adapter,
                use_mechanism_cards=args.use_mechanism_cards,
            )
        report = run_cfdc_route(
            route_id,
            description=description,
            safety_limits=safety_bounds,
            diagnostic_adapter=adapter,
            use_mechanism_cards=args.use_mechanism_cards,
            include_trajectory=args.include_trajectory,
            diagnostic_session_state=session_state,
            diagnostic_answers=(diagnostic_answers or None),
            supplemental_description=args.diagnostic_description,
            measurement_response=measurement_response,
            simulation_bounds_confirmed=args.confirm_simulation_bounds,
            evidence_package=evidence_package,
            specification_text=specification_text,
            execution_mode="demo_fixture" if args.demo_fixture else "user_object",
        )
        trace_reader = getattr(adapter, "agent_trace", None)
        if callable(trace_reader):
            report = report.model_copy(update={"agent_trace": trace_reader()})
        if args.diagnostic_session_output is not None:
            if report.diagnostic_session is None:
                raise SystemExit("route did not produce a diagnostic session state")
            write_diagnostic_session_atomic(
                args.diagnostic_session_output,
                report.diagnostic_session,
            )
        payload = (
            report.model_dump() if args.full_report else compact_route_report(report)
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if not args.description:
        raise SystemExit(
            "Provide --description, use --run-route, --validate-demo, --benchmark, "
            "--feature-ablation, --diagnostic-eval, --diagnostic-eval-llm, "
            "--cartpole-swingup, or --vtol-sim."
        )


if __name__ == "__main__":
    main()
