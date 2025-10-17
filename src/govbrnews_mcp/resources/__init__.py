"""
Resources do servidor MCP GovBRNews.
"""

from .agencies import format_agencies, get_agencies
from .news import format_news, get_news_by_id
from .stats import format_stats, get_stats
from .themes import format_themes, get_themes

__all__ = [
    "get_stats",
    "format_stats",
    "get_agencies",
    "format_agencies",
    "get_themes",
    "format_themes",
    "get_news_by_id",
    "format_news",
]
