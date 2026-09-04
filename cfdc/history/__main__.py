from __future__ import annotations

import argparse
import json

from .core import (
    RECORD_TYPES,
    OperationalHistoryRequest,
    build_history_index,
    load_history_index,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and query an independent CFDC operational-history index"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    index = commands.add_parser("index", help="Build an immutable history snapshot.")
    index.add_argument("--source", required=True, help="Validated history source JSON.")
    index.add_argument("--index-dir", required=True)

    inspect = commands.add_parser(
        "inspect", help="Inspect a snapshot without loading an encoder."
    )
    inspect.add_argument("--index-dir", required=True)
    inspect.add_argument("--snapshot", default=None)

    query = commands.add_parser("query", help="Query one exact operational identity.")
    query.add_argument("--index-dir", required=True)
    query.add_argument("--snapshot", default=None)
    query.add_argument("--plant-id", required=True)
    query.add_argument("--configuration-fingerprint", required=True)
    query.add_argument("--operating-region-fingerprint", required=True)
    query.add_argument(
        "--record-type",
        action="append",
        choices=sorted(RECORD_TYPES),
        default=[],
    )
    query.add_argument("--as-of", default=None)
    query.add_argument("--query", default="")
    query.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    if args.command == "index":
        result = build_history_index(args.source, args.index_dir)
        print(
            json.dumps(
                {
                    "snapshot": result.index_snapshot,
                    "index_dir": str(args.index_dir),
                    "records": result.manifest["record_count"],
                    "embedding_model": result.manifest["embedding_model"],
                },
                ensure_ascii=False,
            )
        )
        return
    if args.command == "inspect":
        result = load_history_index(
            args.index_dir,
            snapshot_name=args.snapshot,
            load_encoder=False,
        ).inspect()
        print(json.dumps(result, ensure_ascii=False))
        return
    history = load_history_index(
        args.index_dir,
        snapshot_name=args.snapshot,
        load_encoder=bool(args.query.strip()),
    )
    request = OperationalHistoryRequest(
        plant_id=args.plant_id,
        configuration_fingerprint=args.configuration_fingerprint,
        operating_region_fingerprint=args.operating_region_fingerprint,
        record_types=tuple(args.record_type),
        as_of=args.as_of,
        query_text=args.query,
        limit=args.limit,
    )
    print(json.dumps(history.query(request).model_dump(), ensure_ascii=False))


if __name__ == "__main__":
    main()
