# LightQnA

LightQnA 是一个基于 LightRAG 的本地医学问答项目。当前主流程使用 Streamlit 提供登录、注册、多轮对话和多语言界面，使用 LightRAG + Neo4j 构建医学知识检索，并支持 Ollama 或 OpenAI 兼容接口作为生成模型。

本项目仅用于本地研究和演示，不应替代专业医疗建议。

## 当前功能

- Streamlit 医学问答界面，入口为 `login.py`
- 用户注册、登录、持久会话和多对话窗口
- SQLite 保存用户、会话和聊天记录，默认路径为 `tmp_data/app.db`
- LightRAG 索引构建、图谱检索和问答
- Neo4j 作为 LightRAG 图存储
- Ollama embedding，默认模型为 `bge-m3:latest`
- 生成模型可选本地 Ollama 或 OpenAI 兼容 API
- 支持中文、日文、英文界面文本
- 提供基础单元测试

## 项目结构

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

## 环境准备

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

## 配置

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

## 构建索引

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

## 运行

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

## 测试

```bash
pytest
```

当前测试覆盖 LightRAG 配置、OpenAI 兼容接口参数、查询参数、用户/会话持久化，以及医学 JSON 到文档文本的转换。

## 本地数据说明

通常不应提交这些本地运行产物：

- `.env`
- `.venv/`
- `lightrag_storage/`
- `tmp_data/app.db*`
- 大模型权重、Neo4j 本地数据目录、缓存文件

如果需要共享大文件，优先使用 Git LFS、外部网盘或文档说明下载方式。

## 更新到 GitHub

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
