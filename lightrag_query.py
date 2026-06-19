"""Query the local LightRAG index without starting Streamlit."""

from __future__ import annotations

import argparse
import asyncio
import logging

from lightrag_adapter import finalize_lightrag, initialize_lightrag, query_lightrag
from logging_setup import setup_logging

logger = logging.getLogger(__name__)


async def run_query(question: str) -> str:
    rag = await initialize_lightrag()
    try:
        return await query_lightrag(rag, question)
    finally:
        await finalize_lightrag(rag)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="查询本地 LightRAG 医疗知识库")
    parser.add_argument("question", help="要查询的医疗问题")
    return parser


def main() -> None:
    setup_logging()
    args = build_parser().parse_args()
    answer = asyncio.run(run_query(args.question))
    logger.info("查询完成")
    print(answer)


if __name__ == "__main__":
    main()
