import os
import sys
from fastmcp import FastMCP
from contextlib import redirect_stdout

# 確保可以正確載入你原本專案的 RAG 工具
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from rag_tool import read_markdown_docs
from logging_config.logger import configure_logging, get_logger

# 1. 初始化 FastMCP Server
mcp = FastMCP("Nanobot-Customer-Service")

@mcp.tool()
def search_customer_service_docs(query: str) -> str:
    """
    查詢平台使用資訊、遊客常見問題與客服知識庫文檔 (RAG)。
    當使用者詢問關於平台操作、功能說明或遊客須知時，必須呼叫此工具獲取正確資訊。
    
    :param query: 想要查詢的關鍵字或問題描述
    """
    try:
        # 使用 logger 輸出，確保 logging 內部的 handler 是朝向 sys.stderr
        logger = get_logger(__name__)
        logger.info(f"MCP 收到查詢請求: {query}")
        
        # 呼叫已經修正能接收參數的 RAG 工具
        if hasattr(read_markdown_docs, "invoke"):
            result = read_markdown_docs.invoke({"query": query})
        else:
            result = read_markdown_docs(query)
            
        return str(result)
        
    except Exception as e:
        return f"查詢文檔時發生錯誤: {str(e)}"

if __name__ == "__main__":
    # 💡 終極解法：使用 contextlib.redirect_stdout 將 FastMCP 啟動時亂噴的橫幅
    # 導向到 sys.stderr（標準錯誤），這樣就不會污染 sys.stdout（標準輸出）的 JSON 管道了！
    with open(os.devnull, "w") as fnull:
        with redirect_stdout(fnull):
            # 移除會報錯的 banner=False，回歸乾淨的 stdio 模式
            mcp.run(transport="stdio")
