from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from llm import ask_model

app = FastAPI(
    title="Regulation Assistant",
    version="0.1.0"
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    needs_clarification: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    # return ChatResponse(
    #     answer=f"Тестовый ответ на запрос: {request.message}",
    #     sources=[],
    #     needs_clarification=False,
    # )

    answer = ask_model(request.message)

    return ChatResponse(
        answer=answer,
        sources=[],
        needs_clarification=False,
    )