from __future__ import annotations

import argparse
import json
from pathlib import Path

from cfdc.knowledge import RetrievalRequest

from .core import build_index, evaluate_retrieval, load_index


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
    evaluation = sub.add_parser(
        "eval", help="Evaluate a labeled retrieval set without an LLM."
    )
    evaluation.add_argument("--index-dir", required=True)
    evaluation.add_argument("--snapshot", default=None)
    evaluation.add_argument(
        "--dataset",
        default=None,
        help="JSON list (or {'cases': [...]}) with relevant_source_ids and request fields.",
    )
    evaluation.add_argument(
        "--split",
        choices=["dev", "holdout"],
        default=None,
        help="Evaluate only cases carrying this split label.",
    )
    args = parser.parse_args()
    if args.command == "index":
        result = build_index(
            args.source_dir,
            args.index_dir,
            include_builtin=not args.no_builtin,
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
