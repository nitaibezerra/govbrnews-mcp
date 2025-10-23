"""
Tools do servidor MCP GovBRNews.
"""

from .search import search_news
from .facets import get_facets
from .similar import similar_news
from .temporal import analyze_temporal

__all__ = [
    "search_news",
    "get_facets",
    "similar_news",
    "analyze_temporal",
]
