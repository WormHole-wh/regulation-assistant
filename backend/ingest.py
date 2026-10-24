from pathlib import Path
import hashlib

import fitz  # PyMuPDF
from docx import Document

from backend.rag import collection, get_embedding

PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_DIR / "data" / "source"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def read_pdf(path: Path) -> list[dict]:
    """Читает PDF с сохранением номеров страниц"""
    pages = []

    with fitz.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "text": text,
                    "section": f"Страница {page_number}",
                })

    return pages


def read_docx(path: Path) -> list[dict]:
    """Читает текст DOCX"""
    document = Document(path)
    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    text = "\n".join(paragraphs)

    if not text:
        return []

    return [{
        "text": text,
        "section": "Текст документа",
    }]


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Разбивает текст на перекрывающиеся фрагменты"""
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def ingest_file(path: Path) -> int:
    """Загружает один PDF или DOCX в ChromaDB"""
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        pages = read_pdf(path)
    elif suffix == ".docx":
        pages = read_docx(path)
    else:
        return 0

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for page in pages:
        chunks = split_text(page["text"])

        for chunk_index, chunk in enumerate(chunks):
            chunk_id = hashlib.sha256(
                f"{path.resolve()}:{page['section']}:{chunk_index}".encode("utf-8")
            ).hexdigest()

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source": path.name,
                "section": page["section"],
            })
            embeddings.append(get_embedding(chunk))

    if not ids:
        return 0

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    return len(ids)


def ingest_all() -> dict:
    """Загружает все PDF и DOCX из data/source/"""
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    files = [
        path for path in SOURCE_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in {".pdf", ".docx"}
    ]

    total_chunks = 0
    processed_files = 0
    errors = []

    for path in files:
        try:
            count = ingest_file(path)
            total_chunks += count
            processed_files += 1
        except Exception as error:
            errors.append({
                "file": path.name,
                "error": str(error),
            })

    return {
        "processed_files": processed_files,
        "total_chunks": total_chunks,
        "errors": errors,
    }


if __name__ == "__main__":
    result = ingest_all()
    print(result)
