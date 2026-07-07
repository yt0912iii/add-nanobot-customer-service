import os
import sys
from fastmcp import FastMCP
from contextlib import redirect_stdout
from mcp.server.stdio import stdio_server  # 💡 確保引入官方的純淨伺服器
import asyncio

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
    # 💡 終極解法：繞過 fastmcp 的 mcp.run() 外殼，直接用最底層的 stdio 引擎啟動。
    # 這能 100% 繞過 FastMCP 內建的橫幅列印機制，只傳輸純淨的 JSON！
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                mcp._mcp_server.create_initialization_options()
            )
            
    # 啟動非同步異步迴圈
    asyncio.run(main())
