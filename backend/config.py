import os

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434" # здесь дефолтное значение для Ollama, поэтому ничего по сути менять не надо
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b"               # какая модель стоит (в консоль вбей ollama list)
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"       # здесь, вроде как, ничего менять не надо, но лучше перепроверь
)