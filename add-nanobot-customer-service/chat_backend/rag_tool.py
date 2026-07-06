import os
from pathlib import Path
from langchain.tools import tool
from logging_config.logger import get_logger

logger = get_logger(__name__)

@tool
def read_markdown_docs(query: str = "") -> str:
    """
    當使用者詢問問題時，一律使用此工具讀取 docs 資料夾底下的 markdown 檔案以尋找答案。
    """
    logger.info("read_markdown_docs tool called")
    
    # 💡 修正：動態取得目前檔案所在的絕對路徑，確保 Cursor 後台啟動時也找得到資料夾
    current_dir = Path(__file__).parent.absolute()
    docs_path = current_dir / "uploadedfiles"

    contents = []

    if not docs_path.exists():
        return f"錯誤：找不到資料夾 {docs_path}"

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
        return "查無資料"
    
    return "\n\n".join(contents)
