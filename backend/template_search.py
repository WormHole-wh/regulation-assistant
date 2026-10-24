
import re

from backend.documents import list_templates, read_template_content


STOP_WORDS = {
    "мне", "нужно", "надо", "для", "про", "при", "по",
    "как", "где", "какой", "какая", "какие", "документ",
    "документа", "документе", "подготовить", "сделать",
    "создать", "оформить", "найти", "нужен", "нужна",
}


def normalize(text: str) -> str:
    """Приводит текст к единому формату"""
    text = text.lower().replace("ё", "е")
    return " ".join(re.findall(r"[а-яa-z0-9]+", text))


def tokenize(text: str) -> list[str]:
    """Выделяет значимые слова"""
    return [
        word
        for word in normalize(text).split()
        if len(word) >= 4 and word not in STOP_WORDS
    ]



def find_matching_templates(query: str, limit: int = 5) -> dict:
    """Ищет шаблоны и ранжирует результаты по совпадению с запросом"""
    query = query.strip()

    if not query:
        return {
            "query": query,
            "count": 0,
            "results": [],
            "message": "Введите, какой документ вы ищете.",
        }

    query_normalized = normalize(query)
    query_words = tokenize(query)
    results = []

    for template in list_templates():
        try:
            details = read_template_content(template["name"])
        except (FileNotFoundError, ValueError):
            continue

        name = template["name"]
        content = details["content"]

        normalized_name = normalize(name)
        normalized_content = normalize(content)

        name_words = normalized_name.split()
        content_words = set(normalized_content.split())

        score = 0
        matched_words = []

        # Полная фраза в названии — сильное совпадение.
        if query_normalized in normalized_name:
            score += 15

        for word in query_words:
            name_match = any(
                token.startswith(word) or word.startswith(token)
                for token in name_words
                if min(len(token), len(word)) >= 4
            )

            content_match = any(
                token.startswith(word) or word.startswith(token)
                for token in content_words
                if min(len(token), len(word)) >= 4
            )

            if name_match:
                score += 5
                matched_words.append(word)
            elif content_match:
                score += 1
                matched_words.append(word)

        # Штрафуем документы, в названии которых нет
        # ни одного значимого слова из запроса.
        if query_words and not any(
            any(
                token.startswith(word) or word.startswith(token)
                for token in name_words
                if min(len(token), len(word)) >= 4
            )
            for word in query_words
        ):
            score -= 2

        if score > 0:
            results.append({
                "name": name,
                "filename": template["filename"],
                "score": score,
                "matched_words": matched_words,
            })

    results.sort(key=lambda item: item["score"], reverse=True)
    results = results[:max(1, min(limit, 20))]

    return {
        "query": query,
        "count": len(results),
        "results": results,
        "message": (
            "Найдены подходящие шаблоны."
            if results
            else "Подходящие шаблоны не найдены. Попробуйте уточнить запрос."
        ),
    }
