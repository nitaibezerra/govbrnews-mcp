"""
Tools do servidor MCP GovBRNews.
"""

from .search import search_news
from .facets import get_facets
from .similar import similar_news

__all__ = [
    "search_news",
    "get_facets",
    "similar_news",
]
