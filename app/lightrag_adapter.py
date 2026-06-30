"""LightRAG integration helpers.

This module keeps LightRAG imports lazy so the rest of the project can still be
imported before ``lightrag-hku`` is installed. Runtime initialization happens in
CLI scripts and Streamlit after the user has prepared Ollama and Neo4j.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
from collections.abc import Coroutine
from typing import Any

from app.config import Settings, settings

logger = logging.getLogger(__name__)


def configure_lightrag_environment(settings_obj: Settings = settings) -> dict[str, str]:
    """Populate environment variables expected by LightRAG storage backends."""
    env_values = {
        "NEO4J_URI": settings_obj.NEO4J_URI,
        "NEO4J_USERNAME": settings_obj.NEO4J_USERNAME,
        "NEO4J_PASSWORD": settings_obj.NEO4J_PASSWORD,
        "NEO4J_DATABASE": settings_obj.NEO4J_DATABASE,
        "LIGHTRAG_GRAPH_STORAGE": settings_obj.LIGHTRAG_GRAPH_STORAGE,
        "SUMMARY_LANGUAGE": settings_obj.SUMMARY_LANGUAGE,
        "ENTITY_EXTRACTION_USE_JSON": settings_obj.ENTITY_EXTRACTION_USE_JSON,
        "MAX_GLEANING": str(settings_obj.LIGHTRAG_ENTITY_EXTRACT_MAX_GLEANING),
        "LLM_TIMEOUT": str(settings_obj.LIGHTRAG_LLM_TIMEOUT),
    }
    for name, value in env_values.items():
        if value is not None and os.getenv(name) in (None, ""):
            os.environ[name] = str(value)
    return env_values


def query_param_kwargs(
    settings_obj: Settings = settings,
    *,
    stream: bool = False,
    conversation_history: list[dict[str, str]] | None = None,
    response_type: str = "Multiple Paragraphs",
) -> dict[str, Any]:
    """Build the plain kwargs used to construct LightRAG ``QueryParam``."""
    return {
        "mode": settings_obj.LIGHTRAG_QUERY_MODE,
        "stream": stream,
        "response_type": response_type,
        "conversation_history": conversation_history or [],
    }


def build_query_param(
    settings_obj: Settings = settings,
    *,
    stream: bool = False,
    conversation_history: list[dict[str, str]] | None = None,
    response_type: str = "Multiple Paragraphs",
):
    """Create a LightRAG ``QueryParam`` instance."""
    from lightrag import QueryParam

    return QueryParam(
        **query_param_kwargs(
            settings_obj,
            stream=stream,
            conversation_history=conversation_history,
            response_type=response_type,
        )
    )


def create_ollama_embedding_func(settings_obj: Settings = settings):
    """Create a decorated LightRAG embedding function backed by Ollama."""
    from lightrag.llm.ollama import ollama_embed
    from lightrag.utils import wrap_embedding_func_with_attrs

    embedding_model = settings_obj.LIGHTRAG_EMBEDDING_MODEL
    ollama_host = settings_obj.LIGHTRAG_OLLAMA_HOST

    @wrap_embedding_func_with_attrs(
        embedding_dim=settings_obj.LIGHTRAG_EMBEDDING_DIM,
        max_token_size=settings_obj.LIGHTRAG_EMBEDDING_MAX_TOKEN_SIZE,
        model_name=embedding_model,
    )
    async def embedding_func(texts: list[str]):
        return await ollama_embed.func(
            texts,
            embed_model=embedding_model,
            host=ollama_host,
        )

    return embedding_func


def create_llm_model_func(settings_obj: Settings = settings):
    """Return the LightRAG LLM callback for the configured provider."""
    provider = settings_obj.LLM_PROVIDER.lower()
    if provider in {"openai", "openai_compatible", "api"}:
        from app.llm_client import openai_compatible_model_complete

        return openai_compatible_model_complete
    if provider == "ollama":
        from lightrag.llm.ollama import ollama_model_complete

        return ollama_model_complete
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings_obj.LLM_PROVIDER}")


def llm_model_kwargs(settings_obj: Settings = settings) -> dict[str, Any]:
    """Build provider-specific LightRAG LLM kwargs."""
    provider = settings_obj.LLM_PROVIDER.lower()
    if provider in {"openai", "openai_compatible", "api"}:
        kwargs: dict[str, Any] = {
            "api_key": settings_obj.LLM_API_KEY,
            "base_url": settings_obj.LLM_API_BASE,
            "temperature": settings_obj.LLM_TEMPERATURE,
            "top_p": settings_obj.LLM_TOP_P,
            "timeout": settings_obj.LIGHTRAG_LLM_TIMEOUT,
        }
        if settings_obj.LLM_MAX_TOKENS > 0:
            kwargs["max_tokens"] = settings_obj.LLM_MAX_TOKENS
        return kwargs

    return {
        "host": settings_obj.LIGHTRAG_OLLAMA_HOST,
        "options": {"num_ctx": settings_obj.LIGHTRAG_NUM_CTX},
    }


async def initialize_lightrag(settings_obj: Settings = settings):
    """Initialize a LightRAG instance with configured LLM, Ollama embeddings, and Neo4j."""
    configure_lightrag_environment(settings_obj)
    os.makedirs(settings_obj.LIGHTRAG_WORKING_DIR, exist_ok=True)

    from lightrag import LightRAG

    rag = LightRAG(
        working_dir=settings_obj.LIGHTRAG_WORKING_DIR,
        llm_model_func=create_llm_model_func(settings_obj),
        llm_model_name=settings_obj.LIGHTRAG_LLM_MODEL,
        llm_model_max_async=settings_obj.LIGHTRAG_LLM_MAX_ASYNC,
        llm_model_kwargs=llm_model_kwargs(settings_obj),
        embedding_func=create_ollama_embedding_func(settings_obj),
        embedding_func_max_async=settings_obj.LIGHTRAG_EMBEDDING_MAX_ASYNC,
        max_parallel_insert=settings_obj.LIGHTRAG_MAX_PARALLEL_INSERT,
        entity_extract_max_gleaning=settings_obj.LIGHTRAG_ENTITY_EXTRACT_MAX_GLEANING,
        graph_storage=settings_obj.LIGHTRAG_GRAPH_STORAGE,
        addon_params={
            "language": settings_obj.SUMMARY_LANGUAGE,
            "entity_types": settings_obj.LIGHTRAG_ENTITY_TYPES,
        },
    )
    await rag.initialize_storages()
    return rag


async def finalize_lightrag(rag) -> None:
    """Close LightRAG storage resources when a short-lived CLI is done."""
    if rag is not None:
        await rag.finalize_storages()


async def query_lightrag(
    rag,
    question: str,
    settings_obj: Settings = settings,
    *,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    """Run one LightRAG query and normalize the answer to a string."""
    result = await rag.aquery(
        question,
        param=build_query_param(
            settings_obj,
            conversation_history=conversation_history,
        ),
    )
    if result is None:
        return (
            "本次查询没有返回有效答案。上游模型可能正在限流或临时不可用，"
            "请稍后重试，或在 .env 中切换到限流更宽松的模型。"
        )
    return str(result)


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run an async LightRAG operation from sync Streamlit/CLI code."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, Any] = {}

    def runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except BaseException as exc:  # pragma: no cover - defensive bridge
            result["error"] = exc

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()
    if "error" in result:
        raise result["error"]
    return result.get("value")
