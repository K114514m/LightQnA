# LightQnA

LightQnA is a medical question-answering system built around LightRAG, Neo4j, Streamlit, and configurable LLM providers. The current main workflow uses LightRAG for indexing, graph extraction, retrieval, and answer generation. The older BERT NER, fixed intent routing, and hand-written Cypher knowledge graph modules are still kept in the repository as legacy/reference code.

This project is intended for local research and demo use. It is not a medical device and should not be used as a substitute for professional medical advice.

## Features

- LightRAG-backed medical QA over structured medical records and text documents.
- Neo4j graph storage for LightRAG entities and relationships.
- Ollama embeddings, with `bge-m3:latest` as the default embedding model.
- Configurable generation model: local Ollama or any OpenAI-compatible chat completions API.
- Streamlit chat UI with login, registration, multiple chat windows, and admin diagnostics.
- CLI tools for building and querying the LightRAG index.
- Legacy medical knowledge graph, BERT NER, and intent-routing modules retained for experimentation.

## Current Architecture

```text
LightQnA/
|-- login.py                  # Streamlit login/register entry point
|-- webui.py                  # Streamlit chat UI backed by LightRAG
|-- config.py                 # Centralized environment-based settings
|-- lightrag_adapter.py       # LightRAG initialization, query, and provider helpers
|-- llm_client.py             # OpenAI-compatible LLM client helpers
|-- build_lightrag_index.py   # Build a LightRAG index from JSON/TXT/MD sources
|-- lightrag_query.py         # Query the LightRAG index from the command line
|-- test_lightrag_adapter.py  # Unit tests for LightRAG helper behavior
|-- data/
|   |-- medical_new_2.json    # Main medical record source for LightRAG indexing
|   |-- medical.json          # Legacy NER/KG source data
|   |-- ner_data_aug.txt      # Legacy NER training data
|   `-- ent_aug/              # Legacy entity dictionaries
|-- ner/                      # Legacy BERT + RNN NER package
|-- kg_client.py              # Legacy Neo4j Cypher query wrapper
|-- intent_router.py          # Legacy table-driven intent router
|-- build_up_graph.py         # Legacy handcrafted KG import script
|-- finetune_demo/            # Experimental fine-tuning examples
|-- model/                    # Local model files and checkpoints
|-- tmp_data/                 # Runtime data, including demo user credentials
|-- lightrag_storage/         # Local LightRAG KV/vector/doc-status files
`-- requirements.txt
```

## Requirements

- Python 3.10 is recommended.
- Neo4j 5.x with Bolt enabled.
- Ollama running locally for embeddings.
- One generation model:
  - local Ollama model, or
  - OpenAI-compatible chat completions API.

Install Ollama models used by the default setup:

```bash
ollama pull bge-m3:latest
ollama pull qwen:32b
```

If your machine cannot run a large local generation model, keep `bge-m3:latest` locally for embeddings and use an OpenAI-compatible API for text generation.

## Setup

Clone the repository:

```bash
git clone https://github.com/K114514m/LightQnA.git
cd LightQnA
```

Create and activate a Python environment:

```bash
python -m venv .venv
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

For GPU PyTorch, install the wheel that matches your CUDA version before or after installing the requirements. The default requirement accepts CPU wheels.

## Configuration

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` for your environment:

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

For local Ollama generation instead of an API:

```env
LLM_PROVIDER=ollama
LIGHTRAG_LLM_MODEL=qwen:32b
LIGHTRAG_OLLAMA_HOST=http://localhost:11434
```

Important settings:

| Variable | Purpose | Default |
|---|---|---|
| `NEO4J_URI` | Neo4j Bolt URI used by LightRAG | `neo4j://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | project-local default, override it |
| `NEO4J_DATABASE` | Neo4j database name | `neo4j` |
| `LLM_PROVIDER` | `ollama` or `openai_compatible` | API if key exists, otherwise Ollama |
| `LLM_API_BASE` | OpenAI-compatible API base URL | `https://api.openai.com/v1` |
| `LLM_API_KEY` | API key for remote generation | empty |
| `LLM_MODEL` | Remote generation model name | `gpt-4o` |
| `LIGHTRAG_LLM_MODEL` | Model name passed to LightRAG | derived from provider |
| `LIGHTRAG_EMBEDDING_MODEL` | Ollama embedding model | `bge-m3:latest` |
| `LIGHTRAG_EMBEDDING_DIM` | Embedding dimension | `1024` |
| `LIGHTRAG_QUERY_MODE` | LightRAG query mode | `mix` |
| `LIGHTRAG_WORKING_DIR` | Local LightRAG storage directory | `./lightrag_storage` |

## Build the LightRAG Index

Start Neo4j and Ollama first. Then run a small smoke test:

```bash
python build_lightrag_index.py --source data/medical_new_2.json --reset --limit 100
```

`--reset` removes the local LightRAG working directory and clears the configured Neo4j database. Use it only when you want a fresh index.

If the smoke test works, build the full index:

```bash
python build_lightrag_index.py --source data/medical_new_2.json --reset
```

You can also index a directory of supported documents:

```bash
python build_lightrag_index.py --source-dir ./docs
```

Supported source formats are `.json`, `.jsonl`, `.txt`, `.md`, and `.markdown`. Medical JSON records are converted into natural-language statements before insertion.

## Query from the CLI

After building the index:

```bash
python lightrag_query.py "What are the symptoms and treatments for pertussis?"
```

The CLI initializes LightRAG, queries the configured Neo4j-backed graph and local storage, prints the answer, and then closes storage resources.

## Run the Streamlit App

Start the UI:

```bash
streamlit run login.py
```

Open the Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

Default demo admin account:

```text
username: admin
password: admin123
```

Registered users and the default admin account are stored in `tmp_data/user_credentials.json`.

## Testing

Run the unit tests:

```bash
pytest
```

The current tests focus on LightRAG adapter configuration, OpenAI-compatible request handling, query parameter construction, and medical JSON-to-document conversion.

## Legacy Modules

The repository still includes the earlier KG + NER implementation:

- `build_up_graph.py` imports predefined medical entities and relationships into Neo4j.
- `kg_client.py` wraps fixed Cypher queries.
- `intent_router.py` maps fixed medical intents to KG queries.
- `ner/`, `ner_model.py`, and `ner_data.py` provide BERT + RNN entity recognition and training utilities.
- `finetune_demo/` contains experimental fine-tuning materials.

These modules are not the default path used by `webui.py`. The current UI queries LightRAG directly and does not run independent BERT NER or fixed 16-class intent routing.

## Data and Storage Notes

- `data/medical_new_2.json` is the primary source used by the LightRAG indexing script.
- `lightrag_storage/` contains local LightRAG runtime files and should normally remain untracked.
- `tmp_data/` contains runtime data such as demo credentials and legacy NER mappings.
- Large model checkpoints should not be committed directly. Use external storage, Git LFS, or local setup instructions instead.
- `.env` contains secrets and must not be committed.

## Security Notes

This project currently stores demo user passwords in plain text in `tmp_data/user_credentials.json`. This is acceptable only for local demos. Before deploying the project, replace this with salted password hashing and a real user/session management layer.

Medical answers are generated from the configured retrieval and LLM pipeline. Always treat output as informational and verify it with qualified medical sources.

## Development Workflow on Another Machine

On a Mac or another development machine:

```bash
git clone https://github.com/K114514m/LightQnA.git
cd LightQnA
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env`, start Neo4j and Ollama, pull the required Ollama models, rebuild or reuse the LightRAG index, and run:

```bash
streamlit run login.py
```

## Acknowledgements

The original medical data and legacy KG design were inspired by public Chinese medical knowledge graph resources and related open-source medical QA projects. The current retrieval workflow is based on LightRAG with Neo4j graph storage.
