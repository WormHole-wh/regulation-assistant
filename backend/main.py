from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.llm import ask_model
from backend.ingest import ingest_all
from backend.documents import list_templates, get_template_info, read_template_content
from backend.approvals import check_approvals
from backend.template_search import find_matching_templates

app = FastAPI(
    title="Regulation Assistant",
    description="Интеллектуальный помощник по внутренним регламентам",
    version="0.2.0",
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


@app.post("/ingest")
def ingest_documents():
    """Загружает документы из data/source в базу знаний"""
    try:
        result = ingest_all()
        return {
            "status": "completed",
            **result,
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка загрузки документов: {str(error)}",
        )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty",
        )

    return ChatResponse(
        answer=f"Тестовый ответ на запрос: {request.message}",
        sources=[],
        needs_clarification=False,
    )

    # answer = ask_model(request.message)
    #
    # return ChatResponse(
    #     answer=answer,
    #     sources=[],
    #     needs_clarification=False,
    # )

@app.get("/templates")
def get_templates():
    """Возвращает список доступных DOCX-модулей"""
    return {"templates": list_templates()}


@app.get("/templates/search")
def search_template_catalog(
    q: str,
    limit: int = 5,
):
    return find_matching_templates(q, limit)


@app.get("/templates/{template_name}")
def get_template(template_name: str):
    """Возвращает информацию о выбранном модуле"""
    try:
        return get_template_info(template_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Модуль не найден",
        )
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


@app.get("/templates/{template_name}/content")
def get_template_content(template_name: str):
    """Возвращает текст выбранного DOCX-модуля"""
    try:
        return read_template_content(template_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Модуль не найден",
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


