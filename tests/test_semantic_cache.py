from src.cache.semantic_cache import SemanticCache


def test_semantic_cache_hits_for_similar_question():
    cache = SemanticCache()

    stored_embedding = [1.0, 0.0, 0.0]
    query_embedding = [0.85, 0.5, 0.0]

    cache.store(
        question='What was Tesla revenue?',
        answer='Tesla revenue increased in 2023.',
        embedding=stored_embedding,
        route='direct',
        sources=['Tesla Financial Report, page 51'],
    )

    result = cache.lookup('How much did Tesla sell?', query_embedding)

    assert result['hit'] is True
    assert result['answer'] == 'Tesla revenue increased in 2023.'


def test_semantic_cache_misses_for_dissimilar_question():
    cache = SemanticCache()

    cache.store(
        question='What was Tesla revenue?',
        answer='Tesla revenue increased in 2023.',
        embedding=[1.0, 0.0, 0.0],
        route='direct',
        sources=['Tesla Financial Report, page 51'],
    )

    result = cache.lookup('What is the weather in Seattle?', [0.0, 0.0, 1.0])

    assert result['hit'] is False
