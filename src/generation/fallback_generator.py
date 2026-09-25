import re
from typing import Any, Dict, List


def grounded_fallback_answer(question: str, route: str, chunks: List[Dict[str, Any]]) -> str:
    if not chunks:
        return 'I could not find sufficient information in the Tesla financial report to answer that reliably.'

    text = ' '.join(chunk.get('text', '') for chunk in chunks[:3])
    sentences = re.split(r'(?<=[.!?])\s+', text)
    answer_parts = []

    for sentence in sentences:
        if len(sentence) < 40:
            continue
        answer_parts.append(sentence.strip())

    summary = ' '.join(answer_parts[:3])
    if not summary:
        summary = text[:500]

    return (
        f'Based on the report excerpts retrieved for this {route} query, the most relevant information is: {summary}\n\n'
        f'This answer is grounded in the supplied Tesla financial report context and does not rely on outside knowledge.'
    )
