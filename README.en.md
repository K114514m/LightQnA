# LightQnA

<details>
<summary><strong>中文</strong></summary>

## 项目简介

LightQnA 是一个基于 LightRAG 的本地医学问答项目，用 Streamlit 提供登录、注册、多轮对话和多语言界面，并通过 LightRAG + Neo4j 构建医学知识检索能力。项目支持本地 Ollama 模型或 OpenAI 兼容 API 作为生成模型。

> 本项目仅用于本地研究和演示，不应替代专业医疗建议。

主要功能：

- 医学问答 Web 界面，入口为 `app/login.py`
- 用户注册、登录、会话保持和多对话窗口
- SQLite 保存用户、会话和聊天记录
- LightRAG 索引构建、图谱检索和问答
- Neo4j 图存储
- Ollama embedding，默认模型为 `bge-m3:latest`
- 生成模型支持本地 Ollama 或 OpenAI 兼容接口
- 中文、日文、英文界面文本

技术栈：

- Python 3.10+
- Streamlit
- LightRAG
- Neo4j
- SQLite
- Ollama
- OpenAI-compatible API
- python-dotenv

## 项目结构

```text
LightQnA/
|-- app/                      # Streamlit 应用和核心业务模块
|   |-- login.py              # 登录、注册和应用入口
|   |-- webui.py              # 医学问答主界面
|   |-- auth_service.py       # 用户、密码哈希和登录会话
|   |-- app_database.py       # SQLite 表结构和连接
|   |-- conversation_store.py # 多对话和消息持久化
|   |-- config.py             # 环境变量配置
|   |-- i18n.py               # 中文、日文、英文界面文案
|   |-- lightrag_adapter.py   # LightRAG 初始化、查询和模型适配
|   |-- llm_client.py         # LLM 客户端封装
|   `-- ui_theme.py           # Streamlit 页面样式
|-- scripts/                  # 索引构建、命令行查询和数据处理脚本
|   |-- build_lightrag_index.py
|   |-- lightrag_query.py
|   `-- processjson.py
|-- assets/img/               # README 和 Web UI 图片资源
|-- data/                     # 医学数据源
|-- requirements.txt          # Python 依赖
`-- .env.example              # 环境变量示例
```

## 运行方法

建议使用 Python 3.10 或更高版本。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

准备本地服务：

- 启动 Neo4j 5.x，并开启 Bolt 连接
- 启动 Ollama
- 准备一个生成模型：本地 Ollama 模型，或 OpenAI 兼容 API

拉取默认 embedding 模型：

```bash
ollama pull bge-m3:latest
```

如果使用本地 Ollama 生成模型，可拉取示例模型：

```bash
ollama pull qwen:32b
```

复制配置文件：

```bash
cp .env.example .env
```

按需修改 `.env`：

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

如果使用本地 Ollama 生成模型：

```env
LLM_PROVIDER=ollama
LIGHTRAG_LLM_MODEL=qwen:32b
LIGHTRAG_OLLAMA_HOST=http://localhost:11434
```

构建 LightRAG 索引：

```bash
python scripts/build_lightrag_index.py --source data/medical_new_2.json --reset
```

启动 Web 应用：

```bash
streamlit run app/login.py
```

浏览器打开终端显示的地址，通常是：

```text
http://localhost:8501
```

默认管理员账号：

```text
username: admin
password: admin123
```

也可以使用命令行查询：

```bash
python scripts/lightrag_query.py "百日咳有哪些症状和治疗方法？"
```

</details>

<details>
<summary><strong>日本語</strong></summary>

## プロジェクト概要

LightQnA は LightRAG をベースにしたローカル医療 Q&A プロジェクトです。Streamlit でログイン、登録、複数ターンの会話、多言語 UI を提供し、LightRAG + Neo4j によって医療知識検索を構築します。生成モデルにはローカル Ollama モデル、または OpenAI 互換 API を利用できます。

> このプロジェクトはローカルでの研究とデモ用途のみを目的としており、専門的な医療助言の代替にはなりません。

主な機能：

- `app/login.py` を入口とする医療 Q&A Web UI
- ユーザー登録、ログイン、セッション保持、複数会話ウィンドウ
- SQLite によるユーザー、セッション、チャット履歴の保存
- LightRAG のインデックス構築、グラフ検索、質問応答
- Neo4j グラフストア
- Ollama embedding。既定モデルは `bge-m3:latest`
- 生成モデルはローカル Ollama または OpenAI 互換 API に対応
- 中国語、日本語、英語の UI テキスト

技術スタック：

- Python 3.10+
- Streamlit
- LightRAG
- Neo4j
- SQLite
- Ollama
- OpenAI-compatible API
- python-dotenv

## プロジェクト構成

```text
LightQnA/
|-- app/                      # Streamlit アプリと主要業務モジュール
|   |-- login.py              # ログイン、登録、アプリ入口
|   |-- webui.py              # 医療 Q&A メイン UI
|   |-- auth_service.py       # ユーザー、パスワードハッシュ、ログインセッション
|   |-- app_database.py       # SQLite テーブル定義と接続
|   |-- conversation_store.py # 複数会話とメッセージの永続化
|   |-- config.py             # 環境変数設定
|   |-- i18n.py               # 中国語、日本語、英語 UI 文言
|   |-- lightrag_adapter.py   # LightRAG 初期化、クエリ、モデルアダプター
|   |-- llm_client.py         # LLM クライアント
|   `-- ui_theme.py           # Streamlit ページスタイル
|-- scripts/                  # インデックス構築、CLI 検索、データ処理スクリプト
|   |-- build_lightrag_index.py
|   |-- lightrag_query.py
|   `-- processjson.py
|-- assets/img/               # README と Web UI の画像リソース
|-- data/                     # 医療データソース
|-- requirements.txt          # Python 依存関係
`-- .env.example              # 環境変数サンプル
```

## 実行方法

Python 3.10 以上を推奨します。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

ローカルサービスを準備します。

- Neo4j 5.x を起動し、Bolt 接続を有効にする
- Ollama を起動する
- 生成モデルを準備する：ローカル Ollama モデル、または OpenAI 互換 API

既定の embedding モデルを取得します。

```bash
ollama pull bge-m3:latest
```

ローカル Ollama 生成モデルを使う場合は、サンプルモデルを取得できます。

```bash
ollama pull qwen:32b
```

設定ファイルをコピーします。

```bash
cp .env.example .env
```

必要に応じて `.env` を編集します。

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

ローカル Ollama 生成モデルを使う場合：

```env
LLM_PROVIDER=ollama
LIGHTRAG_LLM_MODEL=qwen:32b
LIGHTRAG_OLLAMA_HOST=http://localhost:11434
```

LightRAG インデックスを構築します。

```bash
python scripts/build_lightrag_index.py --source data/medical_new_2.json --reset
```

Web アプリを起動します。

```bash
streamlit run app/login.py
```

ブラウザーでターミナルに表示された URL を開きます。通常は次の URL です。

```text
http://localhost:8501
```

既定の管理者アカウント：

```text
username: admin
password: admin123
```

CLI からも検索できます。

```bash
python scripts/lightrag_query.py "百日咳の症状と治療法は？"
```

</details>

<details open>
<summary><strong>English</strong></summary>

## Project Overview

LightQnA is a local medical Q&A project based on LightRAG. It uses Streamlit for login, registration, multi-turn conversations, and a multilingual UI, while LightRAG + Neo4j provide medical knowledge retrieval. The generation model can be either a local Ollama model or an OpenAI-compatible API.

> This project is intended only for local research and demos. It should not replace professional medical advice.

Features:

- Medical Q&A web UI with `app/login.py` as the entry point
- User registration, login, session persistence, and multiple conversation windows
- SQLite persistence for users, sessions, and chat history
- LightRAG index building, graph retrieval, and question answering
- Neo4j graph storage
- Ollama embeddings, with `bge-m3:latest` as the default model
- Generation through local Ollama or an OpenAI-compatible API
- Chinese, Japanese, and English UI text

Tech stack:

- Python 3.10+
- Streamlit
- LightRAG
- Neo4j
- SQLite
- Ollama
- OpenAI-compatible API
- python-dotenv

## Project Structure

```text
LightQnA/
|-- app/                      # Streamlit app and core business modules
|   |-- login.py              # Login, registration, and app entry point
|   |-- webui.py              # Main medical Q&A interface
|   |-- auth_service.py       # Users, password hashing, and login sessions
|   |-- app_database.py       # SQLite table schema and connections
|   |-- conversation_store.py # Conversation and message persistence
|   |-- config.py             # Environment variable configuration
|   |-- i18n.py               # Chinese, Japanese, and English UI text
|   |-- lightrag_adapter.py   # LightRAG initialization, queries, and model adapters
|   |-- llm_client.py         # LLM client wrapper
|   `-- ui_theme.py           # Streamlit page styling
|-- scripts/                  # Indexing, CLI query, and data processing scripts
|   |-- build_lightrag_index.py
|   |-- lightrag_query.py
|   `-- processjson.py
|-- assets/img/               # README and Web UI image assets
|-- data/                     # Medical data sources
|-- requirements.txt          # Python dependencies
`-- .env.example              # Environment variable example
```

## Run

Python 3.10 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Prepare local services:

- Start Neo4j 5.x with Bolt enabled
- Start Ollama
- Prepare a generation model: either a local Ollama model or an OpenAI-compatible API

Pull the default embedding model:

```bash
ollama pull bge-m3:latest
```

If you use a local Ollama generation model, you can pull the example model:

```bash
ollama pull qwen:32b
```

Copy the configuration file:

```bash
cp .env.example .env
```

Edit `.env` as needed:

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

Build the LightRAG index:

```bash
python scripts/build_lightrag_index.py --source data/medical_new_2.json --reset
```

Start the web app:

```bash
streamlit run app/login.py
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

You can also query from the command line:

```bash
python scripts/lightrag_query.py "What are the symptoms and treatments for pertussis?"
```

</details>
