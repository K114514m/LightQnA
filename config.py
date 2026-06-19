"""项目集中配置。

所有外部依赖参数（Neo4j 连接、ollama 模型名、本地模型/数据路径）都通过环境变量
覆盖，未设置时使用与原代码完全一致的默认值，保证零回归。

使用方式::

    from config import settings
    print(settings.NEO4J_URL)

环境变量列表见下方常量定义；亦可参考 README 的「环境变量」章节。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional until requirements are installed
    load_dotenv = None

def _load_dotenv_fallback(path: str | Path | None = None) -> None:
    """Load simple KEY=VALUE pairs when python-dotenv is unavailable."""
    env_path = Path(path) if path is not None else Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    with env_path.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name, value = stripped.split("=", 1)
            name = name.strip()
            value = value.strip().strip('"').strip("'")
            if name and os.getenv(name) in (None, ""):
                os.environ[name] = value


if load_dotenv is not None:
    load_dotenv(Path(__file__).resolve().parent / ".env")
else:
    _load_dotenv_fallback()


def _env(name: str, default: str) -> str:
    """读取环境变量，未设置时返回 default。"""
    value = os.getenv(name)
    return value if value is not None and value != "" else default


def _env_int(name: str, default: int) -> int:
    """读取整数环境变量，格式非法时返回 default。"""
    value = _env(name, str(default))
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    """读取浮点数环境变量，格式非法时返回 default。"""
    value = _env(name, str(default))
    try:
        return float(value)
    except ValueError:
        return default


def _env_list(name: str, default: list[str]) -> list[str]:
    """读取列表环境变量；支持 JSON 数组或逗号分隔字符串。"""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, list):
        items = [str(item).strip() for item in parsed if str(item).strip()]
        return items or default
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or default


@dataclass(frozen=True)
class Settings:
    """运行时配置容器（不可变）。"""

    # --- Neo4j ---
    NEO4J_URL: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    NEO4J_DBNAME: str
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_DATABASE: str

    # --- Ollama LLM ---
    OLLAMA_QWEN_MODEL: str
    OLLAMA_LLAMA_MODEL: str

    # --- API LLM ---
    LLM_PROVIDER: str
    LLM_API_BASE: str
    LLM_API_KEY: str
    LLM_MODEL: str
    LLM_TEMPERATURE: float
    LLM_TOP_P: float
    LLM_MAX_TOKENS: int

    # --- LightRAG ---
    LIGHTRAG_WORKING_DIR: str
    LIGHTRAG_GRAPH_STORAGE: str
    LIGHTRAG_QUERY_MODE: str
    LIGHTRAG_LLM_MODEL: str
    LIGHTRAG_EMBEDDING_MODEL: str
    LIGHTRAG_EMBEDDING_DIM: int
    LIGHTRAG_EMBEDDING_MAX_TOKEN_SIZE: int
    LIGHTRAG_OLLAMA_HOST: str
    LIGHTRAG_NUM_CTX: int
    LIGHTRAG_ENTITY_TYPES: list[str]
    LIGHTRAG_LLM_MAX_ASYNC: int
    LIGHTRAG_EMBEDDING_MAX_ASYNC: int
    LIGHTRAG_MAX_PARALLEL_INSERT: int
    LIGHTRAG_ENTITY_EXTRACT_MAX_GLEANING: int
    LIGHTRAG_LLM_TIMEOUT: int
    SUMMARY_LANGUAGE: str
    ENTITY_EXTRACTION_USE_JSON: str

    # --- 本地模型与数据路径 ---
    NER_MODEL_NAME: str         # HuggingFace BERT 路径（chinese-roberta-wwm-ext）
    NER_CHECKPOINT: str         # 训练好的 NER 权重文件名（不含 .pt 后缀）
    DATA_DIR: str
    TMP_DIR: str
    MODEL_DIR: str

    # --- 日志 ---
    LOG_LEVEL: str


def _build_settings() -> Settings:
    neo4j_user = _env("NEO4J_USER", "neo4j")
    neo4j_password = _env("NEO4J_PASSWORD", "wei8kang7.long")
    neo4j_dbname = _env("NEO4J_DBNAME", "neo4j")
    qwen_model = _env("OLLAMA_QWEN_MODEL", "qwen:32b")
    llm_api_key = _env("LLM_API_KEY", _env("OPENAI_API_KEY", ""))
    llm_api_base = _env("LLM_API_BASE", _env("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    llm_model = _env("LLM_MODEL", _env("OPENAI_MODEL", "gpt-4o"))
    llm_provider_default = "openai_compatible" if llm_api_key else "ollama"
    llm_provider = _env("LLM_PROVIDER", llm_provider_default).strip().lower()
    medical_entity_types = [
        "Disease",
        "Symptom",
        "Drug",
        "Food",
        "Check",
        "Department",
        "Treatment",
        "Producer",
        "Cause",
        "Prevention",
        "Population",
        "Other",
    ]

    return Settings(
        NEO4J_URL=_env("NEO4J_URL", "http://localhost:7474"),
        NEO4J_USER=neo4j_user,
        NEO4J_PASSWORD=neo4j_password,
        NEO4J_DBNAME=neo4j_dbname,
        NEO4J_URI=_env("NEO4J_URI", "neo4j://localhost:7687"),
        NEO4J_USERNAME=_env("NEO4J_USERNAME", neo4j_user),
        NEO4J_DATABASE=_env("NEO4J_DATABASE", neo4j_dbname),
        OLLAMA_QWEN_MODEL=qwen_model,
        OLLAMA_LLAMA_MODEL=_env("OLLAMA_LLAMA_MODEL", "llama2-chinese:13b-chat-q8_0"),
        LLM_PROVIDER=llm_provider,
        LLM_API_BASE=llm_api_base,
        LLM_API_KEY=llm_api_key,
        LLM_MODEL=llm_model,
        LLM_TEMPERATURE=_env_float("LLM_TEMPERATURE", 0.2),
        LLM_TOP_P=_env_float("LLM_TOP_P", 1.0),
        LLM_MAX_TOKENS=_env_int("LLM_MAX_TOKENS", 0),
        LIGHTRAG_WORKING_DIR=_env("LIGHTRAG_WORKING_DIR", "./lightrag_storage"),
        LIGHTRAG_GRAPH_STORAGE=_env("LIGHTRAG_GRAPH_STORAGE", "Neo4JStorage"),
        LIGHTRAG_QUERY_MODE=_env("LIGHTRAG_QUERY_MODE", "mix"),
        LIGHTRAG_LLM_MODEL=_env(
            "LIGHTRAG_LLM_MODEL",
            llm_model if llm_provider != "ollama" else qwen_model,
        ),
        LIGHTRAG_EMBEDDING_MODEL=_env("LIGHTRAG_EMBEDDING_MODEL", "bge-m3:latest"),
        LIGHTRAG_EMBEDDING_DIM=_env_int("LIGHTRAG_EMBEDDING_DIM", 1024),
        LIGHTRAG_EMBEDDING_MAX_TOKEN_SIZE=_env_int("LIGHTRAG_EMBEDDING_MAX_TOKEN_SIZE", 8192),
        LIGHTRAG_OLLAMA_HOST=_env("LIGHTRAG_OLLAMA_HOST", "http://localhost:11434"),
        LIGHTRAG_NUM_CTX=_env_int("LIGHTRAG_NUM_CTX", 32768),
        LIGHTRAG_ENTITY_TYPES=_env_list("LIGHTRAG_ENTITY_TYPES", medical_entity_types),
        LIGHTRAG_LLM_MAX_ASYNC=_env_int("LIGHTRAG_LLM_MAX_ASYNC", 1),
        LIGHTRAG_EMBEDDING_MAX_ASYNC=_env_int("LIGHTRAG_EMBEDDING_MAX_ASYNC", 1),
        LIGHTRAG_MAX_PARALLEL_INSERT=_env_int("LIGHTRAG_MAX_PARALLEL_INSERT", 1),
        LIGHTRAG_ENTITY_EXTRACT_MAX_GLEANING=_env_int("LIGHTRAG_ENTITY_EXTRACT_MAX_GLEANING", 0),
        LIGHTRAG_LLM_TIMEOUT=_env_int("LIGHTRAG_LLM_TIMEOUT", 600),
        SUMMARY_LANGUAGE=_env("SUMMARY_LANGUAGE", "Chinese"),
        ENTITY_EXTRACTION_USE_JSON=_env("ENTITY_EXTRACTION_USE_JSON", "true"),
        NER_MODEL_NAME=_env("NER_MODEL_NAME", "hfl/chinese-roberta-wwm-ext"),
        NER_CHECKPOINT=_env("NER_CHECKPOINT", "best_roberta_rnn_model_ent_aug"),
        DATA_DIR=_env("DATA_DIR", "data"),
        TMP_DIR=_env("TMP_DIR", "tmp_data"),
        MODEL_DIR=_env("MODEL_DIR", "model"),
        LOG_LEVEL=_env("LOG_LEVEL", "INFO"),
    )


# 全局单例：模块导入时即冻结一份当前环境变量快照
settings: Settings = _build_settings()
