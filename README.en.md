# LightQnA

[中文](README.md) | [日本語](README.ja.md) | **English**

LightQnA is a local medical Q&A project based on LightRAG. The current main workflow uses Streamlit for login, registration, multi-turn conversations, and a multilingual UI. It uses LightRAG + Neo4j for medical knowledge retrieval and supports either Ollama or an OpenAI-compatible API as the generation model.

This project is intended only for local research and demos. It should not replace professional medical advice.

## Features

- Streamlit medical Q&A interface, with `login.py` as the entry point
- User registration, login, persistent sessions, and multiple conversation windows
- SQLite persistence for users, sessions, and chat history. The default path is `tmp_data/app.db`
- LightRAG index building, graph retrieval, and question answering
- Neo4j as the LightRAG graph store
- Ollama embeddings, with `bge-m3:latest` as the default model
- Generation model selectable between local Ollama and an OpenAI-compatible API
- Chinese, Japanese, and English UI text
- Basic unit tests

## Project Structure

```text
LightQnA/
|-- login.py                  # Streamlit login/registration entry point
|-- webui.py                  # Main medical Q&A interface
|-- auth_service.py           # Users, password hashing, and login sessions
|-- app_database.py           # SQLite table schema and connections
|-- conversation_store.py     # Conversation and message persistence
|-- i18n.py                   # Chinese/Japanese/English UI text
|-- ui_theme.py               # Streamlit page styling
|-- config.py                 # Environment variable configuration
|-- lightrag_adapter.py       # LightRAG initialization, queries, and model adapters
|-- build_lightrag_index.py   # Build a LightRAG index from JSON/TXT/MD
|-- lightrag_query.py         # Command-line LightRAG query tool
|-- data/medical_new_2.json   # Default medical data source
|-- finetune_demo/            # Fine-tuning experiment materials
|-- requirements.txt
`-- .env.example
```

## Setup

Python 3.10 or 3.11 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Local dependencies:

- Neo4j 5.x with Bolt enabled
- Ollama for embeddings
- A generation model: either a local Ollama model or an OpenAI-compatible API

Default embedding model:

```bash
ollama pull bge-m3:latest
```

If you use a local Ollama generation model, you can also pull the default example model:

```bash
ollama pull qwen:32b
```

## Configuration

Copy the configuration template:

```bash
cp .env.example .env
```

At minimum, review these settings:

```env
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_DATABASE=neo4j

LLM_PROVIDER=openai_compatible
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_MODEL=gpt-4o

LIGHTRAG_EMBEDDING_MODEL=bge-m3:latest
LIGHTRAG_EMBEDDING_DIM=1024
```

If you use a local Ollama generation model:

```env
LLM_PROVIDER=ollama
LIGHTRAG_LLM_MODEL=qwen:32b
LIGHTRAG_OLLAMA_HOST=http://localhost:11434
```

`.env` contains local passwords and API keys. Do not commit it to GitHub.

## Build The Index

Start Neo4j and Ollama first, then run a small smoke test:

```bash
python build_lightrag_index.py --source data/medical_new_2.json --reset --limit 100
```

After confirming it works, build the full index:

```bash
python build_lightrag_index.py --source data/medical_new_2.json --reset
```

`--reset` clears the local LightRAG storage directory and the configured Neo4j database. Use it only when you need to rebuild the index.

You can also index `.json`, `.jsonl`, `.txt`, `.md`, and `.markdown` files from a directory:

```bash
python build_lightrag_index.py --source-dir ./docs
```

## Run

Start the web app:

```bash
streamlit run login.py
```

Open the URL shown in the terminal. It is usually:

```text
http://localhost:8501
```

Default administrator account:

```text
username: admin
password: admin123
```

Command-line query:

```bash
python lightrag_query.py "What are the symptoms and treatments for pertussis?"
```

## Tests

```bash
pytest
```

The current tests cover LightRAG configuration, OpenAI-compatible API parameters, query parameters, user/session persistence, and conversion from medical JSON to document text.

## Local Data Notes

Usually, these local runtime artifacts should not be committed:

- `.env`
- `.venv/`
- `lightrag_storage/`
- `tmp_data/app.db*`
- Model weights, local Neo4j data directories, and cache files

If you need to share large files, prefer Git LFS, external storage, or documentation that explains how to download them.

## Updating GitHub

The repository is already connected to a remote:

```text
origin https://github.com/K114514m/LightQnA.git
```

Typical sync workflow:

```bash
git status --short --branch
git add README.md README.ja.md README.en.md
git commit -m "Add trilingual README files"
git push origin main
```

Before committing:

- Confirm whether deleted old files should really be removed from GitHub
- Do not commit `.venv/`, `.env`, local databases, or index directories
- Be careful with tracked runtime data such as `tmp_data/user_credentials.json` to avoid leaking real account information
- Run `pytest` before pushing, at least to confirm the core logic is still intact
