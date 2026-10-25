import httpx

from backend.config import (
    ANYTHINGLLM_BASE_URL,
    ANYTHINGLLM_API_KEY,
    ANYTHINGLLM_WORKSPACE,
)


def ask_anythingllm(message: str) -> dict:
    if not ANYTHINGLLM_API_KEY:
        raise RuntimeError("Не задан ANYTHINGLLM_API_KEY")

    if not ANYTHINGLLM_WORKSPACE:
        raise RuntimeError("Не задан ANYTHINGLLM_WORKSPACE")

    url = (
        f"{ANYTHINGLLM_BASE_URL}/api/v1/workspace/"
        f"{ANYTHINGLLM_WORKSPACE}/chat"
    )

    response = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {ANYTHINGLLM_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "message": message,
            "mode": "query",
        },
        timeout=90.0,
    )
    response.raise_for_status()

    data = response.json()

    return {
        "answer": data.get("textResponse", ""),
        "sources": data.get("sources", []),
    }
