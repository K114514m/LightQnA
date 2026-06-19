"""OpenAI-compatible chat completion helpers used by LightRAG."""

from __future__ import annotations

import os
from typing import Any

try:
    from config import settings as default_settings
except ImportError:  # pragma: no cover - allows isolated reuse
    default_settings = None


def normalize_openai_base_url(url: str | None) -> str | None:
    """Accept either a base URL or a full chat-completions endpoint."""
    if not url:
        return None
    normalized = url.rstrip("/")
    suffix = "/chat/completions"
    if normalized.endswith(suffix):
        normalized = normalized[: -len(suffix)]
    return normalized


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


OPENAI_CHAT_REQUEST_KEYS = {
    "audio",
    "extra_body",
    "extra_headers",
    "extra_query",
    "frequency_penalty",
    "function_call",
    "functions",
    "logit_bias",
    "logprobs",
    "max_completion_tokens",
    "metadata",
    "modalities",
    "n",
    "parallel_tool_calls",
    "prediction",
    "presence_penalty",
    "reasoning_effort",
    "response_format",
    "seed",
    "service_tier",
    "stop",
    "store",
    "stream",
    "stream_options",
    "timeout",
    "tool_choice",
    "tools",
    "top_logprobs",
    "user",
}


LIGHTRAG_INTERNAL_KEYS = {
    "enable_cot",
    "hashing_kv",
    "keyword_extraction",
    "llm_model_name",
    "model_name",
}


def filter_chat_request_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Keep provider request options and drop LightRAG-only controls."""
    return {
        key: value
        for key, value in kwargs.items()
        if key in OPENAI_CHAT_REQUEST_KEYS and key not in LIGHTRAG_INTERNAL_KEYS
    }


def build_chat_messages(
    prompt: str,
    *,
    system_prompt: str | None = None,
    history_messages: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    """Build a clean OpenAI-compatible messages payload."""
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": str(system_prompt)})

    for message in history_messages or []:
        role = str(message.get("role", "")).strip()
        content = message.get("content")
        if role in {"system", "user", "assistant"} and content:
            messages.append({"role": role, "content": str(content)})

    messages.append({"role": "user", "content": str(prompt)})
    return messages


async def openai_compatible_model_complete(
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list[dict[str, Any]] | None = None,
    keyword_extraction: bool = False,
    **kwargs: Any,
) -> str:
    """Call any OpenAI-compatible chat completion API.

    The signature intentionally mirrors LightRAG's model-complete callbacks.
    Provider secrets are read from kwargs first, then environment variables.
    """
    try:
        from openai import AsyncOpenAI
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError("Missing dependency: install openai or run pip install -r requirements.txt") from exc

    api_key = (
        kwargs.pop("api_key", None)
        or os.getenv("LLM_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or (default_settings.LLM_API_KEY if default_settings is not None else "")
    )
    if not api_key:
        raise RuntimeError("LLM_API_KEY is required when LLM_PROVIDER=openai_compatible")

    base_url = normalize_openai_base_url(
        kwargs.pop("base_url", None) or os.getenv("LLM_API_BASE") or os.getenv("OPENAI_BASE_URL")
        or (default_settings.LLM_API_BASE if default_settings is not None else None)
    )
    model = (
        kwargs.pop("model", None)
        or kwargs.pop("model_name", None)
        or kwargs.pop("llm_model_name", None)
        or os.getenv("LLM_MODEL")
        or os.getenv("OPENAI_MODEL")
        or (default_settings.LLM_MODEL if default_settings is not None else None)
        or "gpt-4o"
    )
    timeout = kwargs.pop("timeout", None)
    temperature = kwargs.pop("temperature", 0.2)
    top_p = kwargs.pop("top_p", 1.0)
    max_tokens = kwargs.pop("max_tokens", None)
    use_response_format = kwargs.pop("use_response_format", None)
    if use_response_format is None:
        use_response_format = _env_bool("LLM_RESPONSE_FORMAT_JSON", False)

    for internal_key in LIGHTRAG_INTERNAL_KEYS:
        kwargs.pop(internal_key, None)

    provider_kwargs = filter_chat_request_kwargs(kwargs)
    client_kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    if timeout:
        client_kwargs["timeout"] = timeout

    request_kwargs: dict[str, Any] = {
        "model": model,
        "messages": build_chat_messages(
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
        ),
        "temperature": temperature,
        "top_p": top_p,
        **provider_kwargs,
    }
    if max_tokens:
        request_kwargs["max_tokens"] = max_tokens
    if keyword_extraction and use_response_format:
        request_kwargs["response_format"] = {"type": "json_object"}

    client = AsyncOpenAI(**client_kwargs)
    response = await client.chat.completions.create(**request_kwargs)
    content = response.choices[0].message.content
    return content or ""


def openai_compatible_generate(
    prompt: str,
    *,
    system_prompt: str | None = None,
    history_messages: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> str:
    """Synchronous helper for legacy data-processing scripts."""
    import asyncio

    return asyncio.run(
        openai_compatible_model_complete(
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            **kwargs,
        )
    )
