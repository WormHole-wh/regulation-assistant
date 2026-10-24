import chromadb
import ollama

from pathlib import Path

from backend.config import OLLAMA_HOST, EMBEDDING_MODEL

ollama_client = ollama.Client(host=OLLAMA_HOST)   # Подключаем Ollama для создания векторных представлений текста

# Создаём локальную базу векторного поиска
PROJECT_DIR = Path(__file__).resolve().parent.parent

chroma_client = chromadb.PersistentClient(
    path=str(PROJECT_DIR / "data" / "chroma")
)

collection = chroma_client.get_or_create_collection(
    name="regulations",
    metadata={"hnsw:space": "cosine"},
)


def get_embedding(text: str) -> list[float]:
    """Преобразует текст в вектор с помощью embedding-модели"""
    response = ollama_client.embed(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response["embeddings"][0]


def search_documents(
    question: str,
    n_results: int = 5,
) -> list[dict]:
    """Находит наиболее подходящие фрагменты документов"""
    if collection.count() == 0:
        return []

    query_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for i, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i] or {}
        distance = results["distances"][0][i]

        matches.append({
            "text": document,
            "source": metadata.get("source", "Неизвестный документ"),
            "section": metadata.get("section", "Не указан"),
            "distance": distance,
        })

    return matches
