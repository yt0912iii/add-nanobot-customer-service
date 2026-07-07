import os
from pathlib import Path
from langchain.tools import tool
from logging_config.logger import get_logger

logger = get_logger(__name__)

# 💡 修正：動態取得目前檔案所在的絕對路徑
current_dir = Path(__file__).parent.absolute()
docs_path = current_dir / "uploadedfiles"

# 🚀 防呆機制：如果資料夾不存在，在初始化時就自動幫你建立好，防止作業系統阻塞卡死！
docs_path.mkdir(parents=True, exist_ok=True)

@tool
def read_markdown_docs(query: str = "") -> str:
    """
    當使用者詢問問題時，一律使用此工具讀取 docs 資料夾底下的 markdown 檔案以尋找答案。
    """
    logger.info("read_markdown_docs tool called")
    
    contents = []

    # 開始掃描自動建立好（或原本就存在）的資料夾
    for file in docs_path.rglob("*.md"):
        content = file.read_text(
            encoding="utf-8",
            errors="ignore"
        )
        contents.append(
            f"""
            # File: {file.name}

            {content}
            """
        )

    if not contents:
        return "知識庫目前為空，請在本地的 uploadedfiles 資料夾中放入 .md 檔案。"
    
    return "\n\n".join(contents)