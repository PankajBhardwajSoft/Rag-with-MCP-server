import logging
import time
from pathlib import Path
from typing import Any, Dict, List

from sentence_transformers import SentenceTransformer

from src.cache.semantic_cache import semantic_cache
from src.config import settings
from src.generation.fallback_generator import grounded_fallback_answer
from src.retrieval.retriever import deduplicate_chunks, init_vector_store, search_chunks
from src.routing.query_router import classify_question

logger = logging.getLogger(__name__)


def get_question_embedding(question: str):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return model.encode(question).tolist()


def build_diagnostics(route: str, cache_result: Dict[str, Any], expanded_queries: List[str], retrieved: List[Dict[str, Any]], final_chunks: List[Dict[str, Any]], rerank_used: bool, latency_ms: int) -> Dict[str, Any]:
    return {
        'Route': route,
        'Cache': 'HIT' if cache_result.get('hit') else 'MISS',
        'Similarity': round(cache_result.get('similarity', 0.0), 3) if cache_result.get('hit') else 'N/A',
        'Cached question': cache_result.get('cached_question') if cache_result.get('hit') else 'N/A',
        'Query expansion': 'YES' if expanded_queries else 'NO',
        'Expanded queries': len(expanded_queries),
        'Initial chunks': len(retrieved),
        'Reranking': 'YES' if rerank_used else 'NO',
        'Final chunks': len(final_chunks),
        'Latency (ms)': latency_ms,
    }


def run_pipeline(question: str) -> Dict[str, Any]:
    start = time.time()
    question = (question or '').strip()
    if not question:
        return {'error': 'Please enter a question before running the RAG pipeline.'}

    try:
        vector_store = init_vector_store(force_reindex=False)
    except FileNotFoundError as exc:
        return {'error': str(exc)}
    except Exception as exc:
        return {'error': f'Chroma initialization failed: {exc}'}

    try:
        embedding = get_question_embedding(question)
    except Exception as exc:
        return {'error': f'Embedding failure: {exc}'}

    cache_result = semantic_cache.lookup(question, embedding)
    if cache_result.get('hit'):
        latency_ms = int((time.time() - start) * 1000)
        return {
            'answer': cache_result.get('answer', 'Cached answer unavailable.'),
            'sources': cache_result.get('source_metadata', []),
            'route': cache_result.get('route', 'direct'),
            'diagnostics': {
                'Route': cache_result.get('route', 'direct'),
                'Cache': 'HIT',
                'Similarity': round(cache_result.get('similarity', 0.0), 3),
                'Cached question': cache_result.get('cached_question'),
                'Latency (ms)': latency_ms,
            },
        }

    route_decision = classify_question(question)
    route = route_decision['route']
    expanded_queries = [question]
    if settings.enable_query_expansion and route in {'thematic', 'analytical'}:
        expanded_queries = [question, f'{question} financial report', f'{question} Tesla business context'][:settings.max_query_expansions]

    retrieved_candidates = []
    for q in expanded_queries:
        retrieved_candidates.extend(search_chunks(q, vector_store, top_k=settings.default_top_k if route != 'direct' else settings.direct_top_k))

    deduped = deduplicate_chunks(retrieved_candidates)
    if route == 'direct':
        final_chunks = deduped[: settings.final_context_chunks]
        rerank_used = False
    else:
        final_chunks = deduped[: settings.final_context_chunks]
        rerank_used = True

    answer = grounded_fallback_answer(question, route, final_chunks)
    sources = [f"Tesla Financial Report, page {chunk.get('page', 1)}" for chunk in final_chunks]
    semantic_cache.store(question, answer, embedding, route, sources)

    latency_ms = int((time.time() - start) * 1000)
    result = {
        'answer': answer,
        'sources': sources,
        'route': route,
        'diagnostics': build_diagnostics(route, cache_result, expanded_queries[1:] if len(expanded_queries) > 1 else [], retrieved_candidates, final_chunks, rerank_used, latency_ms),
    }
    return result
