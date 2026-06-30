# LightQnA

[中文](#中文) | [日本語](#日本語) | [English](#english)

<a id="中文"></a>
## 中文

LightQnA 是一个基于 LightRAG 的本地医学问答项目。当前主流程使用 Streamlit 提供登录、注册、多轮对话和多语言界面，使用 LightRAG + Neo4j 构建医学知识检索，并支持 Ollama 或 OpenAI 兼容接口作为生成模型。

本项目仅用于本地研究和演示，不应替代专业医疗建议。

### 当前功能

- Streamlit 医学问答界面，入口为 `login.py`
- 用户注册、登录、持久会话和多对话窗口
- SQLite 保存用户、会话和聊天记录，默认路径为 `tmp_data/app.db`
- LightRAG 索引构建、图谱检索和问答
- Neo4j 作为 LightRAG 图存储
- Ollama embedding，默认模型为 `bge-m3:latest`
- 生成模型可选本地 Ollama 或 OpenAI 兼容 API
- 支持中文、日文、英文界面文本
- 提供基础单元测试

### 项目结构

```text
LightQnA/
|-- login.py                  # Streamlit 登录/注册入口
|-- webui.py                  # 医学问答主界面
|-- auth_service.py           # 用户、密码哈希和登录会话
|-- app_database.py           # SQLite 表结构和连接
|-- conversation_store.py     # 多对话和消息持久化
|-- i18n.py                   # 中文/日文/英文界面文案
|-- ui_theme.py               # Streamlit 页面样式
|-- config.py                 # 环境变量配置
|-- lightrag_adapter.py       # LightRAG 初始化、查询和模型适配
|-- build_lightrag_index.py   # 从 JSON/TXT/MD 构建 LightRAG 索引
|-- lightrag_query.py         # 命令行查询 LightRAG
|-- data/medical_new_2.json   # 默认医学数据源
|-- finetune_demo/            # 微调实验材料
|-- requirements.txt
`-- .env.example
```

### 环境准备

建议使用 Python 3.10 或 3.11。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

本地依赖：

- Neo4j 5.x，并开启 Bolt 连接
- Ollama，用于 embedding
- 一个生成模型：本地 Ollama 模型，或 OpenAI 兼容 API

默认 embedding 模型：

```bash
ollama pull bge-m3:latest
```

如果使用本地 Ollama 生成模型，可再拉取项目默认示例模型：

```bash
ollama pull qwen:32b
```

### 配置

复制配置模板：

```bash
cp .env.example .env
```

至少需要确认这些配置：

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

`.env` 包含本地密码和 API key，不要提交到 GitHub。

### 构建索引

先启动 Neo4j 和 Ollama，再执行小规模 smoke test：

```bash
python build_lightrag_index.py --source data/medical_new_2.json --reset --limit 100
```

确认正常后构建完整索引：

```bash
python build_lightrag_index.py --source data/medical_new_2.json --reset
```

`--reset` 会清空本地 LightRAG 存储目录，并清空配置的 Neo4j 数据库。只在需要重建索引时使用。

也可以索引目录中的 `.json`、`.jsonl`、`.txt`、`.md`、`.markdown` 文件：

```bash
python build_lightrag_index.py --source-dir ./docs
```

### 运行

启动 Web 应用：

```bash
streamlit run login.py
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

命令行查询：

```bash
python lightrag_query.py "百日咳有哪些症状和治疗方法？"
```

### 测试

```bash
pytest
```

当前测试覆盖 LightRAG 配置、OpenAI 兼容接口参数、查询参数、用户/会话持久化，以及医学 JSON 到文档文本的转换。

### 本地数据说明

通常不应提交这些本地运行产物：

- `.env`
- `.venv/`
- `lightrag_storage/`
- `tmp_data/app.db*`
- 大模型权重、Neo4j 本地数据目录、缓存文件

如果需要共享大文件，优先使用 Git LFS、外部网盘或文档说明下载方式。

### 更新到 GitHub

当前仓库已经绑定远端：

```text
origin https://github.com/K114514m/LightQnA.git
```

常规同步流程：

```bash
git status --short --branch
git add README.md <其他需要提交的文件>
git commit -m "Update project documentation"
git push origin main
```

提交前建议先处理：

- 确认被删除的旧文件是否确实要从 GitHub 删除
- 不要提交 `.venv/`、`.env`、本地数据库和索引目录
- 对 `tmp_data/user_credentials.json` 这类已跟踪的运行数据保持谨慎，避免泄露真实账号信息
- 推送前运行 `pytest`，至少确认核心逻辑未破坏

[Back to top](#lightqna)

<a id="日本語"></a>
## 日本語

LightQnA は LightRAG をベースにしたローカル医療 Q&A プロジェクトです。現在のメインフローでは、Streamlit でログイン、登録、複数ターンの会話、多言語 UI を提供し、LightRAG + Neo4j で医療知識検索を構築します。生成モデルには Ollama または OpenAI 互換 API を利用できます。

このプロジェクトはローカルでの研究とデモ用途のみを目的としており、専門的な医療助言の代替にはなりません。

### 主な機能

- `login.py` を入口とする Streamlit 医療 Q&A UI
- ユーザー登録、ログイン、永続セッション、複数会話ウィンドウ
- SQLite によるユーザー、セッション、チャット履歴の保存。既定パスは `tmp_data/app.db`
- LightRAG のインデックス構築、グラフ検索、質問応答
- LightRAG のグラフストアとして Neo4j を使用
- Ollama embedding。既定モデルは `bge-m3:latest`
- 生成モデルはローカル Ollama または OpenAI 互換 API から選択可能
- 中国語、日本語、英語の UI テキストに対応
- 基本的なユニットテストを提供

### プロジェクト構成

```text
LightQnA/
|-- login.py                  # Streamlit ログイン/登録入口
|-- webui.py                  # 医療 Q&A メイン UI
|-- auth_service.py           # ユーザー、パスワードハッシュ、ログインセッション
|-- app_database.py           # SQLite テーブル定義と接続
|-- conversation_store.py     # 複数会話とメッセージの永続化
|-- i18n.py                   # 中国語/日本語/英語 UI 文言
|-- ui_theme.py               # Streamlit ページスタイル
|-- config.py                 # 環境変数設定
|-- lightrag_adapter.py       # LightRAG 初期化、クエリ、モデルアダプター
|-- build_lightrag_index.py   # JSON/TXT/MD から LightRAG インデックスを構築
|-- lightrag_query.py         # LightRAG コマンドライン検索
|-- data/medical_new_2.json   # 既定の医療データソース
|-- finetune_demo/            # ファインチューニング実験資料
|-- requirements.txt
`-- .env.example
```

### 環境準備

Python 3.10 または 3.11 を推奨します。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

ローカル依存関係：

- Neo4j 5.x。Bolt 接続を有効化してください
- embedding 用の Ollama
- 生成モデル：ローカル Ollama モデル、または OpenAI 互換 API

既定の embedding モデル：

```bash
ollama pull bge-m3:latest
```

ローカル Ollama 生成モデルを使う場合は、プロジェクトの既定サンプルモデルも取得できます。

```bash
ollama pull qwen:32b
```

### 設定

設定テンプレートをコピーします。

```bash
cp .env.example .env
```

少なくとも次の設定を確認してください。

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

`.env` にはローカルパスワードや API キーが含まれるため、GitHub にコミットしないでください。

### インデックス構築

Neo4j と Ollama を起動してから、小規模な smoke test を実行します。

```bash
python build_lightrag_index.py --source data/medical_new_2.json --reset --limit 100
```

問題がなければ完全なインデックスを構築します。

```bash
python build_lightrag_index.py --source data/medical_new_2.json --reset
```

`--reset` はローカルの LightRAG ストレージディレクトリと、設定された Neo4j データベースを消去します。インデックスを再構築する必要がある場合のみ使用してください。

ディレクトリ内の `.json`、`.jsonl`、`.txt`、`.md`、`.markdown` ファイルもインデックス化できます。

```bash
python build_lightrag_index.py --source-dir ./docs
```

### 実行

Web アプリを起動します。

```bash
streamlit run login.py
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

コマンドライン検索：

```bash
python lightrag_query.py "百日咳の症状と治療法は？"
```

### テスト

```bash
pytest
```

現在のテストは、LightRAG 設定、OpenAI 互換 API パラメーター、クエリパラメーター、ユーザー/セッション永続化、医療 JSON からドキュメントテキストへの変換をカバーしています。

### ローカルデータについて

通常、次のローカル実行成果物はコミットしないでください。

- `.env`
- `.venv/`
- `lightrag_storage/`
- `tmp_data/app.db*`
- 大規模モデルの重み、Neo4j ローカルデータディレクトリ、キャッシュファイル

大きなファイルを共有する必要がある場合は、Git LFS、外部ストレージ、またはダウンロード手順を記載したドキュメントを優先してください。

### GitHub への更新

現在のリポジトリにはリモートが設定されています。

```text
origin https://github.com/K114514m/LightQnA.git
```

通常の同期手順：

```bash
git status --short --branch
git add README.md <other files to commit>
git commit -m "Update project documentation"
git push origin main
```

コミット前の確認事項：

- 削除された古いファイルが GitHub から削除されてもよいか確認する
- `.venv/`、`.env`、ローカルデータベース、インデックスディレクトリをコミットしない
- `tmp_data/user_credentials.json` のような追跡済み実行データは、実アカウント情報の漏えいを避けるため慎重に扱う
- push 前に `pytest` を実行し、少なくとも主要ロジックが壊れていないことを確認する

[Back to top](#lightqna)

<a id="english"></a>
## English

LightQnA is a local medical Q&A project based on LightRAG. The current main workflow uses Streamlit for login, registration, multi-turn conversations, and a multilingual UI. It uses LightRAG + Neo4j for medical knowledge retrieval and supports either Ollama or an OpenAI-compatible API as the generation model.

This project is intended only for local research and demos. It should not replace professional medical advice.

### Features

- Streamlit medical Q&A interface, with `login.py` as the entry point
- User registration, login, persistent sessions, and multiple conversation windows
- SQLite persistence for users, sessions, and chat history. The default path is `tmp_data/app.db`
- LightRAG index building, graph retrieval, and question answering
- Neo4j as the LightRAG graph store
- Ollama embeddings, with `bge-m3:latest` as the default model
- Generation model selectable between local Ollama and an OpenAI-compatible API
- Chinese, Japanese, and English UI text
- Basic unit tests

### Project Structure

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

### Setup

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

### Configuration

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

### Build The Index

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

### Run

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

### Tests

```bash
pytest
```

The current tests cover LightRAG configuration, OpenAI-compatible API parameters, query parameters, user/session persistence, and conversion from medical JSON to document text.

### Local Data Notes

Usually, these local runtime artifacts should not be committed:

- `.env`
- `.venv/`
- `lightrag_storage/`
- `tmp_data/app.db*`
- Model weights, local Neo4j data directories, and cache files

If you need to share large files, prefer Git LFS, external storage, or documentation that explains how to download them.

### Updating GitHub

The repository is already connected to a remote:

```text
origin https://github.com/K114514m/LightQnA.git
```

Typical sync workflow:

```bash
git status --short --branch
git add README.md <other files to commit>
git commit -m "Update project documentation"
git push origin main
```

Before committing:

- Confirm whether deleted old files should really be removed from GitHub
- Do not commit `.venv/`, `.env`, local databases, or index directories
- Be careful with tracked runtime data such as `tmp_data/user_credentials.json` to avoid leaking real account information
- Run `pytest` before pushing, at least to confirm the core logic is still intact

[Back to top](#lightqna)
