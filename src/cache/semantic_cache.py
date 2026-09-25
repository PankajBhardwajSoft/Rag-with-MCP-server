import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.config import settings


@dataclass
class CacheEntry:
    cache_id: str
    original_question: str
    answer: str
    question_embedding: List[float]
    created_at: float
    expires_at: float
    route: str
    source_metadata: List[str] = field(default_factory=list)


class SemanticCache:
    def __init__(self):
        self._entries: Dict[str, CacheEntry] = {}

    def _is_expired(self, entry: CacheEntry) -> bool:
        return time.time() > entry.expires_at

    def _cosine_similarity(self, left: List[float], right: List[float]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        norm_a = (sum(a * a for a in left)) ** 0.5
        norm_b = (sum(b * b for b in right)) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def lookup(self, question: str, question_embedding: List[float]) -> Dict[str, Any]:
        now = time.time()
        best_match: Optional[CacheEntry] = None
        best_similarity = 0.0

        for entry in list(self._entries.values()):
            if self._is_expired(entry):
                del self._entries[entry.cache_id]
                continue
            similarity = self._cosine_similarity(question_embedding, entry.question_embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = entry

        if best_match is None or best_similarity < settings.semantic_cache_threshold:
            return {
                'hit': False,
                'similarity': best_similarity,
                'cached_question': None,
                'answer': None,
                'route': None,
            }

        return {
            'hit': True,
            'similarity': best_similarity,
            'cached_question': best_match.original_question,
            'answer': best_match.answer,
            'route': best_match.route,
            'source_metadata': best_match.source_metadata,
        }

    def store(self, question: str, answer: str, embedding: List[float], route: str, sources: List[str]) -> None:
        expired = time.time()
        cache_id = str(abs(hash(question.strip().lower())))
        self._entries[cache_id] = CacheEntry(
            cache_id=cache_id,
            original_question=question,
            answer=answer,
            question_embedding=embedding,
            created_at=expired,
            expires_at=expired + settings.semantic_cache_ttl_seconds,
            route=route,
            source_metadata=sources,
        )


semantic_cache = SemanticCache()
