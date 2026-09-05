"""Export API types without touching live operation metadata or starting RAG."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Also support `python scripts/export_web_openapi.py` from a source checkout.
REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))

from cfdc.web.api import create_app


def main() -> None:
    destination = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else REPOSITORY / "cfdc/web/frontend/openapi.json"
    )
    with tempfile.TemporaryDirectory(prefix="cfdc-openapi-") as temporary:
        root = Path(temporary)
        app = create_app(
            session_dir=root / "sessions", runtime_dir=root / "web", prepare_rag=False
        )
        try:
            schema = app.openapi()
        finally:
            app.state.operations.close()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(destination)


if __name__ == "__main__":
    main()
