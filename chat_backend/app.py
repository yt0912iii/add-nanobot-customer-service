

from urllib import response

from fastapi import FastAPI

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from logging_config.logger import configure_logging, get_logger


from rag_tool import read_markdown_docs
from schemas import ChatRequest, ChatResponse

logger = get_logger(__name__)
configure_logging()
app = FastAPI()


llm = ChatOpenAI(
    model="cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit",  # 只是標籤，可隨便但建議一致
    temperature=0,
    openai_api_key="empty",  # vLLM 不驗證 key
    openai_api_base="http://192.168.50.62:8787/v1"
)



tools = [read_markdown_docs]


prompt = """
            你是智慧客服，你的使命是為遊客查詢平台使用資訊。
            ## 絕對禁止
            - 提供未經工具確認或推測的資訊

            ## 核心原則
            - 必須調用 read_markdown_docs 工具: 每次回答前必須調用 read_markdown_docs 工具獲取文檔，回答內容需要佐證資料，不能直接回答
            - 查無資料時誠實告知，絕不猜測推測

            ## 回應原則
            - 必須以繁體中文回應
            - 回應時不要有額外的說明，直接給出答案
            - 字數限制: ~100字
            - 對於閒聊、無關問題、情緒聊天、不具業務價值的內容，不進行延伸對話
        """


agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=prompt,
    checkpointer=InMemorySaver(),
)





@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        thread_config = {"configurable": {"thread_id": req.request_id}}
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": req.question}]},
            thread_config,
        )
        result = response["messages"][-1].content

        return ChatResponse(answer=result)
    except Exception as e:
        logger.error(f"Error occurred while processing chat request: {str(e)}")
        return ChatResponse(answer=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)