from __future__ import annotations

import argparse
from collections.abc import Sequence

import uvicorn

from cfdc.web.api import create_app


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local CFDC React application."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    uvicorn.run(
        create_app(), host=args.host, port=args.port, workers=1, access_log=False
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
