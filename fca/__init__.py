"""FCA package."""

from .context import FormalContext, load_context_from_json
from .algorithms import build_concepts_set, build_concepts_bitset, compare_implementations

__all__ = [
    'FormalContext',
    'load_context_from_json',
    'save_context_to_json',
    'build_concepts_set',
    'build_concepts_bitset',
    'compare_implementations',
]