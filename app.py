from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from cfdc.web.rag_startup import BuiltinRAGStartupError, prepare_builtin_rag_index
from cfdc.web.ui import CSS, build_app


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CFDC Gradio application.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    print("正在准备并预热内置 RAG 知识库……", flush=True)
    try:
        prepared_rag = prepare_builtin_rag_index()
    except BuiltinRAGStartupError as exc:
        print(f"WebUI 启动失败：{exc}", file=sys.stderr, flush=True)
        return 1
    print(f"内置 RAG 已就绪：{prepared_rag.snapshot}", flush=True)
    build_app(prepared_rag=prepared_rag).queue(default_concurrency_limit=2).launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True,
        css=CSS,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
