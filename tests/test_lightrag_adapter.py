from types import SimpleNamespace
import asyncio

from app.lightrag_adapter import configure_lightrag_environment, llm_model_kwargs, query_param_kwargs
from app.lightrag_adapter import query_lightrag
from app.llm_client import build_chat_messages, filter_chat_request_kwargs, normalize_openai_base_url
from scripts.build_lightrag_index import medical_record_to_text, parse_json_line


def _settings(**overrides):
    values = {
        "NEO4J_URI": "neo4j://example:7687",
        "NEO4J_USERNAME": "neo4j_user",
        "NEO4J_PASSWORD": "neo4j_password",
        "NEO4J_DATABASE": "neo4j_db",
        "LIGHTRAG_GRAPH_STORAGE": "Neo4JStorage",
        "SUMMARY_LANGUAGE": "Chinese",
        "ENTITY_EXTRACTION_USE_JSON": "true",
        "LIGHTRAG_ENTITY_EXTRACT_MAX_GLEANING": 0,
        "LIGHTRAG_QUERY_MODE": "mix",
        "LLM_PROVIDER": "ollama",
        "LLM_API_KEY": "",
        "LLM_API_BASE": "https://api.openai.com/v1",
        "LLM_TEMPERATURE": 0.2,
        "LLM_TOP_P": 1.0,
        "LLM_MAX_TOKENS": 0,
        "LIGHTRAG_LLM_MODEL": "qwen:32b",
        "LIGHTRAG_LLM_TIMEOUT": 600,
        "LIGHTRAG_OLLAMA_HOST": "http://localhost:11434",
        "LIGHTRAG_NUM_CTX": 32768,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_configure_lightrag_environment_sets_missing_values(monkeypatch):
    monkeypatch.delenv("NEO4J_URI", raising=False)
    monkeypatch.delenv("NEO4J_USERNAME", raising=False)
    settings = _settings()

    env_values = configure_lightrag_environment(settings)

    assert env_values["NEO4J_URI"] == "neo4j://example:7687"
    assert env_values["ENTITY_EXTRACTION_USE_JSON"] == "true"
    assert env_values["SUMMARY_LANGUAGE"] == "Chinese"


def test_query_param_kwargs_defaults_to_mix_mode():
    kwargs = query_param_kwargs(_settings(), conversation_history=[{"role": "user", "content": "hi"}])

    assert kwargs["mode"] == "mix"
    assert kwargs["stream"] is False
    assert kwargs["response_type"] == "Multiple Paragraphs"
    assert kwargs["conversation_history"] == [{"role": "user", "content": "hi"}]


def test_query_lightrag_returns_readable_message_for_none_result():
    class EmptyRag:
        async def aquery(self, question, param):
            return None

    answer = asyncio.run(query_lightrag(EmptyRag(), "test", _settings()))

    assert "没有返回有效答案" in answer


def test_llm_model_kwargs_uses_openai_compatible_settings():
    kwargs = llm_model_kwargs(
        _settings(
            LLM_PROVIDER="openai_compatible",
            LLM_API_KEY="test-key",
            LLM_API_BASE="https://example.com/v1",
            LIGHTRAG_LLM_MODEL="large-model",
            LLM_MAX_TOKENS=2048,
        )
    )

    assert kwargs["api_key"] == "test-key"
    assert kwargs["base_url"] == "https://example.com/v1"
    assert kwargs["max_tokens"] == 2048
    assert "host" not in kwargs


def test_normalize_openai_base_url_accepts_chat_completions_endpoint():
    assert (
        normalize_openai_base_url("https://aihubmix.com/v1/chat/completions")
        == "https://aihubmix.com/v1"
    )
    assert normalize_openai_base_url("https://aihubmix.com/v1") == "https://aihubmix.com/v1"


def test_filter_chat_request_kwargs_drops_lightrag_internal_controls():
    filtered = filter_chat_request_kwargs(
        {
            "enable_cot": True,
            "hashing_kv": object(),
            "stop": ["</answer>"],
            "seed": 1,
            "unknown": "ignored",
        }
    )

    assert filtered == {"stop": ["</answer>"], "seed": 1}


def test_build_chat_messages_keeps_history_order():
    messages = build_chat_messages(
        "现在回答",
        system_prompt="你是医疗助手",
        history_messages=[
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好，请问哪里不舒服？"},
            {"role": "tool", "content": "ignored"},
        ],
    )

    assert messages == [
        {"role": "system", "content": "你是医疗助手"},
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，请问哪里不舒服？"},
        {"role": "user", "content": "现在回答"},
    ]


def test_parse_json_line_accepts_legacy_trailing_comma():
    parsed = parse_json_line('{"name": "百日咳", "symptom": ["咳嗽"]},')

    assert parsed == {"name": "百日咳", "symptom": ["咳嗽"]}


def test_medical_record_to_text_converts_record_to_document():
    text = medical_record_to_text(
        {
            "_id": {"$oid": "ignored"},
            "name": "百日咳",
            "desc": "急性呼吸道传染病。",
            "symptom": ["咳嗽", "低热"],
            "recommand_drug": ["红霉素"],
            "drug_detail": ["示例红霉素片,示例药业"],
        }
    )

    assert "疾病：百日咳。" in text
    assert "百日咳 的疾病简介是 急性呼吸道传染病。" in text
    assert "咳嗽 是 百日咳 的症状。" in text
    assert "低热 是 百日咳 的症状。" in text
    assert "红霉素 是 百日咳 的推荐药品。" in text
    assert "示例药业 是 示例红霉素片 的生产商。" in text
    assert "示例红霉素片 是 百日咳 的相关药品。" in text
    assert "$oid" not in text
