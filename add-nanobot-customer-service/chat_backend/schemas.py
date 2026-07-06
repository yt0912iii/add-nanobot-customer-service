from pydantic import BaseModel

class ChatRequest(BaseModel):
    request_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str