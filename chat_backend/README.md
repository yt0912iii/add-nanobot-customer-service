# Chat Backend

FastAPI 聊天機器人後端，使用 LangChain Agent + LLM 提供智慧客服查詢。

## 環境需求

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)（Python 套件管理器）

## 安裝 uv

```bash
# 使用 pip 安裝（通用，Windows / Linux / macOS 皆適用）
pip install uv
```

### Windows

```powershell
# 獨立安裝（不需預裝 Python）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Linux / macOS

```bash
# 獨立安裝
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 啟動虛擬環境與安裝相依套件

### Windows

```powershell
uv sync
.venv\Scripts\activate
```

### Linux / macOS

```bash
uv sync
source .venv/bin/activate
```

## 啟動專案

```bash
# 方式一：直接執行 app.py（需先在虛擬環境中）
python app.py

# 方式二：使用 uvicorn 直接啟動（需先在虛擬環境中）
uvicorn app:app --host localhost --port 8000 --reload

# 方式三：使用 uv run 直接執行（不需先 activate）
uv run uvicorn app:app --host localhost --port 8000 --reload
```

啟動後 API 位於 `http://localhost:8000`。

## API 文件

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## MCP Installation

```json
{
  "mcpServers": {
    "nanobot-customer-service": {
      "command": "uv",
      "args": [
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```