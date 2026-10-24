import ollama

from backend.config import OLLAMA_HOST, OLLAMA_MODEL

client = ollama.Client(host=OLLAMA_HOST)


def ask_model(question: str) -> str:
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": question
            }
        ],
    )

    return response["message"]["content"]
