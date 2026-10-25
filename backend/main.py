import httpx

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.documents import (
    list_templates,
    get_template_info,
    read_template_content,
)
from backend.approvals import check_approvals
from backend.template_search import find_matching_templates
from backend.anythingllm import ask_anythingllm


app = FastAPI(
    title="Regulation Assistant",
    description="Внутренний помощник по регламентам",
    version="0.3.0",
)


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


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
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Сообщение не может быть пустым",
        )

    try:
        result = ask_anythingllm(message)

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=502,
            detail=f"AnythingLLM вернул ошибку HTTP {error.response.status_code}",
        )

    except (httpx.RequestError, RuntimeError):
        raise HTTPException(
            status_code=503,
            detail="Не удалось подключиться к AnythingLLM. Проверь настройки API.",
        )

    answer = result.get("answer") or "AnythingLLM не вернул текст ответа."

    return ChatResponse(
        answer=answer,
        sources=result.get("sources", []),
        needs_clarification=False,
    )


@app.get("/templates")
def get_templates():
    return {"templates": list_templates()}


@app.get("/templates/search")
def search_template_catalog(q: str, limit: int = 5):
    return find_matching_templates(q, limit)


@app.get("/templates/{template_name}/content")
def get_template_content(template_name: str):
    try:
        return read_template_content(template_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Шаблон не найден",
        )


@app.get("/templates/{template_name}")
def get_template(template_name: str):
    try:
        return get_template_info(template_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Шаблон не найден",
        )
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


class ApprovalRequest(BaseModel):
    document_type: str
    changes_system_access: bool = False
    it_project: bool = False


@app.post("/approvals/check")
def check_document_approvals(request: ApprovalRequest):
    return check_approvals(
        document_type=request.document_type,
        changes_system_access=request.changes_system_access,
        it_project=request.it_project,
    )


# Подключаем frontend
app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)
