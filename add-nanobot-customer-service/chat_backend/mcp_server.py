import os
import sys
from fastmcp import FastMCP

# 確保可以正確載入你原本專案的 RAG 工具
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from rag_tool import read_markdown_docs
from logging_config.logger import configure_logging, get_logger

# 初始化日誌
logger = get_logger(__name__)
configure_logging()

# 1. 初始化 FastMCP Server（移除導致報錯的 dependencies 參數）
mcp = FastMCP("Nanobot-Customer-Service")

# 2. 將你原本的 RAG 技能註冊為 MCP Tool
@mcp.tool()
def search_customer_service_docs(query: str) -> str:
    """
    查詢平台使用資訊、遊客常見問題與客服知識庫文檔 (RAG)。
    當使用者詢問關於平台操作、功能說明或遊客須知時，必須呼叫此工具獲取正確資訊。
    
    :param query: 想要查詢的關鍵字或問題描述
    """
    try:
        logger.info(f"MCP 收到查詢請求: {query}")
        
        # 3. 呼叫原本寫好的 RAG 工具
        if hasattr(read_markdown_docs, "invoke"):
            result = read_markdown_docs.invoke(query)
        else:
            result = read_markdown_docs(query)
            
        return str(result)
        
    except Exception as e:
        logger.error(f"RAG 查詢失敗: {str(e)}")
        return f"查詢文檔時發生錯誤: {str(e)}"

if __name__ == "__main__":
    # 4. 以標準 stdio 模式啟動
    mcp.run(transport="stdio")