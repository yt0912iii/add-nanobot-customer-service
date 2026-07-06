from pathlib import Path

from langchain.tools import tool

from logging_config.logger import get_logger

logger = get_logger(__name__)

@tool
def read_markdown_docs() -> str:
    """
    When user ask question alawys use this tool to read markdown files under docs folder to find answer.
    Read all markdown files under docs folder.
    """
    logger.info("read_markdown_docs tool called")
    docs_path = Path("uploadedfiles")

    contents = []

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