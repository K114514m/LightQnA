"""Build a LightRAG index from medical JSON records or unstructured documents."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import shutil
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from config import settings
from lightrag_adapter import finalize_lightrag, initialize_lightrag
from logging_setup import setup_logging

logger = logging.getLogger(__name__)

FIELD_LABELS = {
    "name": "疾病名称",
    "desc": "疾病简介",
    "category": "所属分类",
    "prevent": "预防措施",
    "cause": "病因",
    "symptom": "症状",
    "yibao_status": "医保状态",
    "get_prob": "发病概率",
    "easy_get": "易感人群",
    "get_way": "传播方式",
    "acompany": "并发疾病",
    "cure_department": "就诊科室",
    "cure_way": "治疗方法",
    "cure_lasttime": "治疗周期",
    "cured_prob": "治愈概率",
    "cost_money": "治疗费用",
    "check": "检查项目",
    "common_drug": "常用药品",
    "recommand_drug": "推荐药品",
    "do_eat": "宜吃食物",
    "not_eat": "忌吃食物",
    "recommand_eat": "推荐食谱",
    "drug_detail": "药品生产商信息",
}

RELATION_SENTENCE_FIELDS = {
    "category": "所属分类",
    "symptom": "症状",
    "acompany": "并发疾病",
    "cure_department": "就诊科室",
    "cure_way": "治疗方法",
    "check": "检查项目",
    "common_drug": "常用药品",
    "recommand_drug": "推荐药品",
    "do_eat": "宜吃食物",
    "not_eat": "忌吃食物",
    "recommand_eat": "推荐食谱",
}

ATTRIBUTE_SENTENCE_FIELDS = {
    "desc": "疾病简介是",
    "prevent": "预防措施是",
    "cause": "病因是",
    "yibao_status": "医保状态是",
    "get_prob": "发病概率是",
    "easy_get": "易感人群是",
    "get_way": "传播方式是",
    "cure_lasttime": "治疗周期是",
    "cured_prob": "治愈概率是",
    "cost_money": "治疗费用是",
}

TEXT_SUFFIXES = {".txt", ".md", ".markdown"}
JSON_SUFFIXES = {".json", ".jsonl"}


def parse_json_line(line: str) -> dict[str, Any] | None:
    """Parse one JSON/JSONL line, accepting legacy trailing commas."""
    cleaned = line.strip().rstrip(",")
    if not cleaned:
        return None
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _format_value(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, list):
        items = [_format_value(item) for item in value]
        return "、".join(item for item in items if item)
    if isinstance(value, dict):
        parts = [
            f"{key}: {_format_value(inner)}"
            for key, inner in value.items()
            if key != "$oid" and _format_value(inner)
        ]
        return "；".join(parts)
    return str(value).strip()


def _sentence(subject: str, predicate: str, value: Any) -> str:
    formatted = _format_value(value)
    if not formatted:
        return ""
    return f"{subject} 的{predicate} {formatted}。"


def _iter_values(value: Any) -> list[str]:
    """Return cleaned scalar values without joining list items."""
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [formatted for item in value if (formatted := _format_value(item))]
    formatted = _format_value(value)
    return [formatted] if formatted else []


def _relation_sentences(subject: str, relation_name: str, value: Any) -> list[str]:
    """Convert list-like fields into one binary relation sentence per item."""
    return [
        f"{item} 是 {subject} 的{relation_name}。"
        for item in _iter_values(value)
    ]


def _drug_detail_sentences(subject: str, value: Any) -> list[str]:
    """Convert producer/drug detail values into relation-like sentences."""
    if not isinstance(value, list):
        formatted = _format_value(value)
        return [f"{subject} 的药品生产商信息包括 {formatted}。"] if formatted else []

    sentences: list[str] = []
    for item in value:
        formatted = _format_value(item)
        if not formatted:
            continue
        if "," in formatted:
            drug, producer = [part.strip() for part in formatted.split(",", 1)]
            if drug and producer:
                sentences.append(f"{producer} 是 {drug} 的生产商。")
                sentences.append(f"{drug} 是 {subject} 的相关药品。")
                continue
        sentences.append(f"{subject} 的药品生产商信息包括 {formatted}。")
    return sentences


def medical_record_to_text(record: dict[str, Any]) -> str:
    """Convert one structured record into natural-language text for LightRAG."""
    title = _format_value(record.get("name")) or "未命名医疗记录"
    sections = [f"疾病：{title}。"]

    for key, predicate in ATTRIBUTE_SENTENCE_FIELDS.items():
        sentence = _sentence(title, predicate, record.get(key))
        if sentence:
            sections.append(sentence)

    for key, relation_name in RELATION_SENTENCE_FIELDS.items():
        sections.extend(_relation_sentences(title, relation_name, record.get(key)))

    sections.extend(_drug_detail_sentences(title, record.get("drug_detail")))

    for key, value in record.items():
        if key in {"_id", "name", "drug_detail"}:
            continue
        if key in ATTRIBUTE_SENTENCE_FIELDS or key in RELATION_SENTENCE_FIELDS:
            continue
        sentence = _sentence(title, f"{FIELD_LABELS.get(key, key)}是", value)
        if sentence:
            sections.append(sentence)
    return "\n".join(sections)


def iter_json_documents(path: Path) -> Iterator[str]:
    """Yield LightRAG-ready documents from JSON arrays, JSON objects, or JSONL."""
    raw_text = path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict):
        yield medical_record_to_text(parsed)
        return
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict):
                yield medical_record_to_text(item)
            elif item:
                yield str(item)
        return

    for line in raw_text.splitlines():
        record = parse_json_line(line)
        if record:
            yield medical_record_to_text(record)


def iter_file_documents(path: Path) -> Iterator[str]:
    """Yield documents from one file."""
    suffix = path.suffix.lower()
    if suffix in JSON_SUFFIXES:
        yield from iter_json_documents(path)
    elif suffix in TEXT_SUFFIXES:
        text = path.read_text(encoding="utf-8").strip()
        if text:
            yield text


def iter_documents(
    *,
    source: Path | None,
    source_dir: Path | None,
    limit: int | None,
) -> Iterator[str]:
    """Yield documents from the configured source file and/or directory."""
    count = 0
    paths: list[Path] = []
    if source is not None:
        paths.append(source)
    if source_dir is not None:
        paths.extend(
            path
            for path in sorted(source_dir.rglob("*"))
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES | JSON_SUFFIXES
        )

    for path in paths:
        if not path.exists():
            logger.warning("跳过不存在的路径: %s", path)
            continue
        for document in iter_file_documents(path):
            if document.strip():
                yield document
                count += 1
                if limit is not None and count >= limit:
                    return


def batched(items: Iterable[str], batch_size: int) -> Iterator[list[str]]:
    batch: list[str] = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def reset_local_storage() -> None:
    """Remove local LightRAG KV/vector/doc-status files."""
    working_dir = Path(settings.LIGHTRAG_WORKING_DIR)
    if working_dir.exists():
        shutil.rmtree(working_dir)


def reset_neo4j_graph() -> None:
    """Clear the configured Neo4j database for a fresh LightRAG graph."""
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
    )
    try:
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            session.run("MATCH (n) DETACH DELETE n").consume()
    finally:
        driver.close()


async def build_index(args: argparse.Namespace) -> int:
    if args.reset:
        logger.warning("重置 LightRAG 本地存储和 Neo4j 图数据库")
        reset_local_storage()
        if settings.LIGHTRAG_GRAPH_STORAGE == "Neo4JStorage":
            reset_neo4j_graph()

    source = Path(args.source) if args.source else None
    source_dir = Path(args.source_dir) if args.source_dir else None
    documents = iter_documents(source=source, source_dir=source_dir, limit=args.limit)

    rag = await initialize_lightrag()
    inserted = 0
    try:
        for batch in batched(documents, args.batch_size):
            await rag.ainsert(batch)
            inserted += len(batch)
            logger.info("已插入 %d 个文档", inserted)
    finally:
        await finalize_lightrag(rag)
    logger.info("LightRAG 索引构建完成，共插入 %d 个文档", inserted)
    return inserted


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="使用 LightRAG 从医疗文档构建知识图谱")
    parser.add_argument("--source", default="data/medical_new_2.json", help="JSON/JSONL/TXT/MD 源文件")
    parser.add_argument("--source-dir", default=None, help="包含 TXT/MD/JSON/JSONL 的文档目录")
    parser.add_argument("--limit", type=int, default=None, help="最多插入多少个文档，便于 smoke test")
    parser.add_argument("--batch-size", type=int, default=4, help="每批提交给 LightRAG 的文档数")
    parser.add_argument("--reset", action="store_true", help="清空 LightRAG 本地存储和 Neo4j 图数据库")
    return parser


def main() -> None:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(build_index(args))


if __name__ == "__main__":
    main()
