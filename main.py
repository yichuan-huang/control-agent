from __future__ import annotations

import argparse
import json

from cfdc.diagnosis import OpenAICompatibleDiagnosticAdapter
from cfdc.diagnosis import run_diagnostic_evaluation
from cfdc.demo import run_demo_validation
from cfdc.models import CFDCRunReport, SystemDescription
from cfdc.pipeline import run_cfdc_pipeline
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the independent CFDC framework.")
    parser.add_argument("--description", type=str, help="Plain-language system description.")
    parser.add_argument("--observed-output", action="append", default=[], help="Measured output name. Can be repeated.")
    parser.add_argument("--actuator", action="append", default=[], help="Actuator or input name. Can be repeated.")
    parser.add_argument("--benchmark", action="store_true", help="Run the built-in CFDC synthetic benchmark chain.")
    parser.add_argument("--feature-ablation", action="store_true", help="Run minimal/noisy/full-model feature ablations.")
    parser.add_argument("--diagnostic-eval", action="store_true", help="Score the saved 8+4 offline diagnostic responses.")
    parser.add_argument("--diagnostic-eval-current", action="store_true", help="Score fresh deterministic diagnostic responses.")
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
    parser.add_argument("--use-llm", action="store_true", help="Use an OpenAI-compatible LLM for Stage 0 diagnosis.")
    parser.add_argument(
        "--use-mechanism-cards",
        action="store_true",
        help="Add optional mechanism-card labels without changing the canonical archetype route.",
    )
    parser.add_argument("--llm-base-url", type=str, default=None, help="OpenAI-compatible base URL, e.g. https://api.openai.com/v1.")
    parser.add_argument("--llm-model", type=str, default=None, help="OpenAI-compatible model name.")
    parser.add_argument("--llm-api-key", type=str, default=None, help="API key. Prefer environment variables for normal use.")
    parser.add_argument("--llm-timeout-s", type=float, default=60.0, help="LLM request timeout in seconds.")
    parser.add_argument("--llm-max-tokens", type=int, default=1400, help="Maximum diagnostic response tokens.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    adapter = None
    if args.use_llm:
        adapter = OpenAICompatibleDiagnosticAdapter(
            base_url=args.llm_base_url,
            model=args.llm_model,
            api_key=args.llm_api_key,
            timeout_s=args.llm_timeout_s,
            max_tokens=args.llm_max_tokens,
        )

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
    if args.cartpole_swingup:
        print(json.dumps(simulate_cartpole_energy_swingup(include_trajectory=False).model_dump(), indent=2, sort_keys=True))
        return
    if args.vtol_sim:
        print(json.dumps(run_vtol_simulation(mode=args.vtol_mode, include_trajectory=args.include_trajectory).model_dump(), indent=2, sort_keys=True))
        return
    if args.run_route:
        description = None
        if args.description:
            description = SystemDescription(
                text=args.description,
                observed_outputs=args.observed_output,
                actuators=args.actuator,
            )
        report = run_cfdc_route(
            args.run_route,
            description=description,
            diagnostic_adapter=adapter,
            use_mechanism_cards=args.use_mechanism_cards,
            include_trajectory=args.include_trajectory,
        )
        payload = report.model_dump() if args.full_report else compact_route_report(report)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if not args.description:
        raise SystemExit(
            "Provide --description, use --run-route, --validate-demo, --benchmark, "
            "--feature-ablation, --diagnostic-eval, --cartpole-swingup, or --vtol-sim."
        )
    description = SystemDescription(
        text=args.description,
        observed_outputs=args.observed_output,
        actuators=args.actuator,
    )
    print(
        json.dumps(
            run_cfdc_pipeline(
                description,
                diagnostic_adapter=adapter,
                use_mechanism_cards=args.use_mechanism_cards,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
