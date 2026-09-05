"""Serve the built frontend and real API with disposable validation data."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uvicorn

from cfdc.web.api import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=7867)
    parser.add_argument("--prepare-rag", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="cfdc-web-e2e-") as temporary:
        root = Path(temporary)
        os.environ["CFDC_RAG_INDEX_DIR"] = str(root / "rag-index")
        uvicorn.run(
            create_app(
                session_dir=root / "sessions",
                runtime_dir=root / "web",
                prepare_rag=args.prepare_rag,
            ),
            host="127.0.0.1",
            port=args.port,
            access_log=False,
        )


if __name__ == "__main__":
    main()
