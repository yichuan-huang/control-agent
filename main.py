from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from uuid import uuid4

from cfdc.diagnosis import (
    OpenAICompatibleDiagnosticAdapter,
    start_diagnostic_session,
)
from cfdc.diagnosis import (
    run_diagnostic_evaluation,
    run_live_llm_diagnostic_comparison,
    run_saved_llm_diagnostic_comparison,
)
from cfdc.demo import run_demo_validation
from cfdc.models import (
    CFDCRunReport,
    DiagnosticSessionState,
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
            raise SystemExit(
                f"invalid --safety-bound {item!r}; expected KEY=FLOAT"
            )
        if key in bounds:
            raise SystemExit(f"duplicate --safety-bound key '{key}'")
        try:
            value = float(raw_value)
        except ValueError:
            raise SystemExit(
                f"invalid --safety-bound {item!r}; value must be a float"
            ) from None
        if not math.isfinite(value):
            raise SystemExit(
                f"invalid --safety-bound {item!r}; value must be finite"
            )
        bounds[key] = value
    return bounds


def load_diagnostic_session(path: Path) -> DiagnosticSessionState:
    try:
        return DiagnosticSessionState.model_validate_json(
            path.read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as exc:
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
    parser.add_argument("--description", type=str, help="Plain-language system description.")
    parser.add_argument("--observed-output", action="append", default=[], help="Measured output name. Can be repeated.")
    parser.add_argument("--actuator", action="append", default=[], help="Actuator or input name. Can be repeated.")
    parser.add_argument("--safety-bound", action="append", default=[], metavar="KEY=FLOAT", help="Safety bound. Can be repeated.")
    parser.add_argument("--time-scale-hint-s", type=_positive_float, default=None, help="Positive process time-scale hint in seconds.")
    parser.add_argument("--diagnostic-session-input", type=Path, default=None, help="Resume a DiagnosticSessionState JSON file.")
    parser.add_argument("--diagnostic-session-output", type=Path, default=None, help="Atomically write the resulting DiagnosticSessionState JSON file.")
    parser.add_argument("--diagnostic-answer", action="append", default=[], metavar="QUESTION_ID=ANSWER", help="Answer a pending question by stable question ID.")
    parser.add_argument("--diagnostic-description", type=str, default=None, help="Add a free-form supplemental description when resuming a diagnostic session.")
    parser.add_argument("--benchmark", action="store_true", help="Run the built-in CFDC synthetic benchmark chain.")
    parser.add_argument("--feature-ablation", action="store_true", help="Run minimal/noisy/full-model feature ablations.")
    parser.add_argument("--diagnostic-eval", action="store_true", help="Score the saved 8+4 offline diagnostic responses.")
    parser.add_argument("--diagnostic-eval-current", action="store_true", help="Score fresh deterministic diagnostic responses.")
    parser.add_argument("--diagnostic-eval-llm", action="store_true", help="Call the configured LLM for all frozen 8+4 cases, save structured responses, and compare with deterministic results.")
    parser.add_argument("--diagnostic-eval-llm-saved", action="store_true", help="Compare a previously saved LLM response snapshot with the deterministic baseline.")
    parser.add_argument("--diagnostic-llm-output", type=Path, default=None, help="Optional path for the structured LLM diagnostic response snapshot.")
    parser.add_argument("--validate-demo", action="store_true", help="Validate the stable Cartpole and VTOL software demo routes.")
    parser.add_argument("--cartpole-swingup", action="store_true", help="Run the deterministic cartpole energy swing-up simulation.")
    parser.add_argument("--vtol-sim", action="store_true", help="Run the deterministic planar VTOL simulation.")
    parser.add_argument("--vtol-mode", choices=["altitude", "hover", "position", "boundary"], default="position", help="Planar VTOL simulation mode.")
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
    parser.add_argument("--include-trajectory", action="store_true", help="Include route simulation trajectories in JSON output.")
    parser.add_argument("--full-report", action="store_true", help="Include raw experiment traces and trial samples in route JSON output.")
    parser.add_argument("--use-llm", action="store_true", help="Use the configured OpenAI-compatible provider for diagnosis and closed-catalog profile selection.")
    parser.add_argument(
        "--use-mechanism-cards",
        action="store_true",
        help="Add optional mechanism-card labels without changing the canonical archetype route.",
    )
    parser.add_argument("--llm-base-url", type=str, default=None, help="Provider API root, e.g. https://api.deepseek.com/v1 or http://localhost:11434/v1 (env: CFDC_LLM_BASE_URL).")
    parser.add_argument("--llm-model", type=str, default=None, help="Provider model identifier (env: CFDC_LLM_MODEL).")
    parser.add_argument("--llm-api-key", type=str, default=None, help="Provider API key (env: CFDC_LLM_API_KEY). Prefer environment variables for normal use.")
    parser.add_argument("--llm-timeout-s", type=float, default=60.0, help="LLM request timeout in seconds.")
    parser.add_argument("--llm-max-tokens", type=int, default=1400, help="Maximum diagnostic response tokens.")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    safety_bounds = parse_safety_bounds(args.safety_bound)
    session_state = (
        load_diagnostic_session(args.diagnostic_session_input)
        if args.diagnostic_session_input is not None
        else None
    )
    diagnostic_answers = parse_diagnostic_answers(args.diagnostic_answer)
    if diagnostic_answers and session_state is None:
        raise SystemExit("--diagnostic-answer requires --diagnostic-session-input")
    adapter = None
    if args.use_llm or args.diagnostic_eval_llm:
        try:
            adapter = OpenAICompatibleDiagnosticAdapter(
                base_url=args.llm_base_url,
                model=args.llm_model,
                api_key=args.llm_api_key,
                timeout_s=args.llm_timeout_s,
                max_tokens=args.llm_max_tokens,
            )
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
        print(json.dumps(run_feature_ablation_suite().model_dump(mode="json"), indent=2, sort_keys=True))
        return
    if args.diagnostic_eval or args.diagnostic_eval_current:
        result = run_diagnostic_evaluation(
            use_saved_responses=not args.diagnostic_eval_current,
        )
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
        return
    if args.diagnostic_eval_llm:
        if adapter is None:
            raise RuntimeError("LLM diagnostic evaluation requires a configured adapter")
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
        print(json.dumps(simulate_cartpole_energy_swingup(include_trajectory=False).model_dump(), indent=2, sort_keys=True))
        return
    if args.vtol_sim:
        print(json.dumps(run_vtol_simulation(mode=args.vtol_mode, include_trajectory=args.include_trajectory).model_dump(), indent=2, sort_keys=True))
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
        route_id = args.run_route or (session_state.route_id if session_state is not None else "generic")
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
        )
        if args.diagnostic_session_output is not None:
            if report.diagnostic_session is None:
                raise SystemExit("route did not produce a diagnostic session state")
            write_diagnostic_session_atomic(
                args.diagnostic_session_output,
                report.diagnostic_session,
            )
        payload = report.model_dump() if args.full_report else compact_route_report(report)
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
