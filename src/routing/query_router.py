import json
import re

from src.config import settings


def classify_question(question: str) -> dict:
    text = question.strip().lower()
    if not text:
        return {'route': 'direct', 'reason': 'Empty question.', 'confidence': 0.0}

    analytical_markers = ['compare', 'comparison', 'across years', 'difference', 'change', 'why', 'explain changes', 'opportunities and risks', 'financial performance']
    direct_markers = ['revenue', 'margin', 'cash', 'profit', 'loss', 'deliveries', 'operating income', 'debt', 'expenses', 'cost', 'balance sheet', 'when', 'what was', 'how much', 'how many']
    thematic_markers = ['strategy', 'business', 'drivers', 'risks', 'growth', 'energy', 'production', 'business model', 'story', 'overview', 'approach', 'market']

    if any(marker in text for marker in analytical_markers):
        route = 'analytical'
        reason = 'The question compares metrics, changes, or multiple factors across the report.'
        confidence = 0.9
    elif any(marker in text for marker in direct_markers):
        route = 'direct'
        reason = 'The question requests a specific fact or narrowly scoped financial value.'
        confidence = 0.88
    elif any(marker in text for marker in thematic_markers):
        route = 'thematic'
        reason = 'The question asks for a broader business theme, strategy, or risk summary.'
        confidence = 0.8
    else:
        route = 'thematic'
        reason = 'Defaulting to the broader thematic route due to limited certainty.'
        confidence = 0.6

    return {
        'route': route,
        'reason': reason,
        'confidence': min(confidence, 0.99),
    }
