from __future__ import annotations

import argparse

from cfdc.web.ui import CSS, build_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CFDC Gradio application.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_app().queue(default_concurrency_limit=2).launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True,
        css=CSS,
    )
