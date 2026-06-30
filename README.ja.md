# LightQnA

[中文](README.md) | **日本語** | [English](README.en.md)

LightQnA は LightRAG をベースにしたローカル医療 Q&A プロジェクトです。現在のメインフローでは、Streamlit でログイン、登録、複数ターンの会話、多言語 UI を提供し、LightRAG + Neo4j で医療知識検索を構築します。生成モデルには Ollama または OpenAI 互換 API を利用できます。

このプロジェクトはローカルでの研究とデモ用途のみを目的としており、専門的な医療助言の代替にはなりません。

## 主な機能

- `login.py` を入口とする Streamlit 医療 Q&A UI
- ユーザー登録、ログイン、永続セッション、複数会話ウィンドウ
- SQLite によるユーザー、セッション、チャット履歴の保存。既定パスは `tmp_data/app.db`
- LightRAG のインデックス構築、グラフ検索、質問応答
- LightRAG のグラフストアとして Neo4j を使用
- Ollama embedding。既定モデルは `bge-m3:latest`
- 生成モデルはローカル Ollama または OpenAI 互換 API から選択可能
- 中国語、日本語、英語の UI テキストに対応
- 基本的なユニットテストを提供

## プロジェクト構成

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

## 環境準備

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

## 設定

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

## インデックス構築

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

## 実行

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

## テスト

```bash
pytest
```

現在のテストは、LightRAG 設定、OpenAI 互換 API パラメーター、クエリパラメーター、ユーザー/セッション永続化、医療 JSON からドキュメントテキストへの変換をカバーしています。

## ローカルデータについて

通常、次のローカル実行成果物はコミットしないでください。

- `.env`
- `.venv/`
- `lightrag_storage/`
- `tmp_data/app.db*`
- 大規模モデルの重み、Neo4j ローカルデータディレクトリ、キャッシュファイル

大きなファイルを共有する必要がある場合は、Git LFS、外部ストレージ、またはダウンロード手順を記載したドキュメントを優先してください。

## GitHub への更新

現在のリポジトリにはリモートが設定されています。

```text
origin https://github.com/K114514m/LightQnA.git
```

通常の同期手順：

```bash
git status --short --branch
git add README.md README.ja.md README.en.md
git commit -m "Add trilingual README files"
git push origin main
```

コミット前の確認事項：

- 削除された古いファイルが GitHub から削除されてもよいか確認する
- `.venv/`、`.env`、ローカルデータベース、インデックスディレクトリをコミットしない
- `tmp_data/user_credentials.json` のような追跡済み実行データは、実アカウント情報の漏えいを避けるため慎重に扱う
- push 前に `pytest` を実行し、少なくとも主要ロジックが壊れていないことを確認する
