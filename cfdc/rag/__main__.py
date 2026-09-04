from __future__ import annotations

import argparse
import json
from pathlib import Path

from cfdc.knowledge import RetrievalRequest

from .core import build_index, evaluate_retrieval, load_index
from .knowledge_pack import load_knowledge_pack

_ACCEPTANCE_METRICS = {
    "artifact_group_recall_at_4_min": "artifact_group_recall_at_4",
    "artifact_group_mrr_min": "artifact_group_mrr",
    "irrelevant_result_rate_max": "irrelevant_result_rate",
    "negative_query_false_positive_rate_max": ("negative_query_false_positive_rate"),
    "artifact_group_duplicate_rate_max": "artifact_group_duplicate_rate",
    "provenance_resolution_rate_min": "provenance_resolution_rate",
    "preferred_language_hit_rate_min": "preferred_language_hit_rate",
    "bilingual_group_duplicate_rate_max": "bilingual_group_duplicate_rate",
    "override_error_rate_max": "override_error_rate",
}


def _acceptance_failures(
    report: dict[str, object], acceptance: dict[str, object]
) -> list[str]:
    failures: list[str] = []
    for gate, metric in _ACCEPTANCE_METRICS.items():
        if gate not in acceptance:
            continue
        actual = float(report[metric])
        expected = float(acceptance[gate])
        if (gate.endswith("_min") and actual < expected) or (
            gate.endswith("_max") and actual > expected
        ):
            failures.append(f"{metric}={actual:.6f} violates {gate}={expected:.6f}")
    for metric in (
        "duplicate_rate",
        "artifact_group_duplicate_rate",
        "bilingual_group_duplicate_rate",
        "override_error_rate",
        "scope_leakage_rate",
        "stale_result_rate",
    ):
        if float(report[metric]) != 0.0:
            failures.append(f"{metric} must equal zero")
    if float(report["provenance_resolution_rate"]) != 1.0:
        failures.append("provenance_resolution_rate must equal one")
    return failures


def main():
    parser = argparse.ArgumentParser(description="Build a local CFDC RAG index")
    sub = parser.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index")
    index.add_argument(
        "--source-dir",
        required=False,
        help="Explicit PDF/Markdown directory; omit for built-in knowledge only.",
    )
    index.add_argument("--index-dir", required=True)
    index.add_argument(
        "--no-builtin",
        action="store_true",
        help="Index only the explicitly supplied PDF/Markdown directory.",
    )
    curated = index.add_mutually_exclusive_group()
    curated.add_argument(
        "--knowledge-pack",
        help="Validated knowledge-pack directory; defaults to the bundled pack.",
    )
    curated.add_argument(
        "--no-curated",
        action="store_true",
        help="Do not include the bundled curated knowledge pack.",
    )
    index.add_argument(
        "--relevance-threshold",
        type=float,
        default=None,
        help="Explicit immutable snapshot relevance threshold from 0 to 1.",
    )
    inspect = sub.add_parser(
        "inspect", help="Inspect a snapshot without embedding work."
    )
    inspect.add_argument("--index-dir", required=True)
    inspect.add_argument("--snapshot", default=None)
    query = sub.add_parser("query", help="Query a snapshot for retrieval diagnostics.")
    query.add_argument("--index-dir", required=True)
    query.add_argument("--query", required=True)
    query.add_argument("--role", default="legacy")
    query.add_argument("--operation", default="query")
    query.add_argument("--stage", default=None)
    query.add_argument("--class", dest="canonical_class", default=None)
    query.add_argument("--profile", dest="profile_id", default=None)
    query.add_argument("--language", choices=["auto", "en", "zh"], default="auto")
    evaluation = sub.add_parser(
        "eval", help="Evaluate a labeled retrieval set without an LLM."
    )
    evaluation.add_argument("--index-dir", required=True)
    evaluation.add_argument("--snapshot", default=None)
    dataset_source = evaluation.add_mutually_exclusive_group()
    dataset_source.add_argument(
        "--dataset",
        default=None,
        help="JSON list (or {'cases': [...]}) with relevant_source_ids and request fields.",
    )
    dataset_source.add_argument(
        "--bundled",
        action="store_true",
        help="Evaluate the immutable datasets shipped with the knowledge pack.",
    )
    evaluation.add_argument(
        "--suite",
        default=None,
        help="Evaluate one bundled dataset instead of every bundled dataset.",
    )
    evaluation.add_argument(
        "--split",
        choices=["dev", "holdout"],
        default=None,
        help="Evaluate only cases carrying this split label.",
    )
    evaluation.add_argument(
        "--assert-acceptance",
        action="store_true",
        help="Exit nonzero if any bundled quality gate is not met.",
    )
    args = parser.parse_args()
    if args.command == "index":
        result = build_index(
            args.source_dir,
            args.index_dir,
            include_builtin=not args.no_builtin,
            include_curated=not args.no_curated,
            knowledge_pack_dir=args.knowledge_pack,
            relevance_threshold=args.relevance_threshold,
        )
        print(
            json.dumps(
                {
                    "snapshot": result.index_snapshot,
                    "index_dir": str(args.index_dir),
                    "chunks": result.manifest.get("chunk_count", 0),
                    "embedding_model": result.manifest.get("embedding_model"),
                },
                ensure_ascii=False,
            )
        )
    elif args.command == "inspect":
        print(
            json.dumps(
                load_index(
                    args.index_dir,
                    snapshot_name=args.snapshot,
                    load_encoder=False,
                ).inspect(),
                ensure_ascii=False,
            )
        )
    elif args.command == "query":
        index = load_index(args.index_dir)
        request = RetrievalRequest(
            role=args.role,
            operation=args.operation,
            stage=args.stage,
            canonical_class=args.canonical_class,
            profile_id=args.profile_id,
            summary=args.query,
            language=args.language,
        )
        print(
            json.dumps(
                [
                    {
                        "source_id": row.source_id,
                        "source_path": row.source_path,
                        "section": row.section,
                        "page": row.page,
                        "artifact_type": row.artifact_type,
                        "artifact_id": row.artifact_id,
                        "artifact_group_id": row.artifact_group_id,
                        "source_kind": row.source_kind,
                        "language": row.language,
                        "authority": row.authority,
                        "artifact_version": row.artifact_version,
                        "canonical_classes": list(row.canonical_classes),
                        "profile_ids": list(row.profile_ids),
                        "citation_refs": [dict(item) for item in row.citation_refs],
                        "score": row.score,
                        "dense_score": row.dense_score,
                        "lexical_score": row.lexical_score,
                        "text": row.text,
                    }
                    for row in index.retrieve(request)
                ],
                ensure_ascii=False,
            )
        )
    elif args.command == "eval":
        if args.suite and not args.bundled:
            raise SystemExit("--suite requires --bundled")
        if args.assert_acceptance and not args.bundled:
            raise SystemExit("--assert-acceptance requires --bundled")
        if args.bundled:
            pack = load_knowledge_pack()
            datasets = list(pack.evaluation["datasets"])
            if args.suite:
                datasets = [
                    dataset
                    for dataset in datasets
                    if dataset["dataset_id"] == args.suite
                ]
            else:
                datasets = [
                    dataset
                    for dataset in datasets
                    if dataset.get("purpose") != "regression"
                ]
            if not datasets:
                raise SystemExit("requested bundled evaluation suite is unavailable")
            datasets = [
                dataset
                for dataset in datasets
                if any(
                    args.split is None or case.get("split") == args.split
                    for case in dataset["cases"]
                )
            ]
            if not datasets:
                raise SystemExit("no bundled evaluation cases match the selected split")
            index = load_index(args.index_dir, snapshot_name=args.snapshot)
            reports = {
                str(dataset["dataset_id"]): evaluate_retrieval(
                    index,
                    dataset["cases"],
                    split=args.split,
                )
                for dataset in datasets
            }
            combined_cases = [case for dataset in datasets for case in dataset["cases"]]
            combined = evaluate_retrieval(index, combined_cases, split=args.split)
            acceptance = dict(pack.evaluation_metadata["acceptance"])
            failures = {
                name: rejected
                for name, report in [*reports.items(), ("combined", combined)]
                if (rejected := _acceptance_failures(report, acceptance))
            }
            payload = {
                "snapshot": index.index_snapshot,
                "split": args.split,
                "reports": reports,
                "combined": combined,
                "acceptance": acceptance,
                "failures": failures,
                "passed": not failures,
            }
            print(json.dumps(payload, ensure_ascii=False))
            if args.assert_acceptance and failures:
                raise SystemExit(1)
            return
        if args.dataset:
            dataset_path = Path(args.dataset)
            try:
                payload = json.loads(dataset_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise SystemExit(f"unable to read evaluation dataset: {exc}") from exc
            cases = payload.get("cases") if isinstance(payload, dict) else payload
            if not isinstance(cases, list) or not all(
                isinstance(item, dict) for item in cases
            ):
                raise SystemExit(
                    "evaluation dataset must be a JSON list of objects or {'cases': [...]}."
                )
            index = load_index(args.index_dir, snapshot_name=args.snapshot)
            print(
                json.dumps(
                    evaluate_retrieval(index, cases, split=args.split),
                    ensure_ascii=False,
                )
            )
            return
        index = load_index(
            args.index_dir, snapshot_name=args.snapshot, load_encoder=False
        )
        policy = index.manifest.get("retrieval_policy", {})
        print(
            json.dumps(
                {
                    "snapshot": index.index_snapshot,
                    "policy": policy,
                    "message": "Provide a separate labeled dev/holdout set to calibrate and report Recall@4/false-positive rate.",
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
