"""
Resource para notícia individual do dataset GovBRNews.
"""

import logging
from typing import Any

from ..typesense_client import get_typesense_client
from ..utils.formatters import format_timestamp

logger = logging.getLogger(__name__)


def get_news_by_id(news_id: str) -> dict[str, Any]:
    """
    Obtém notícia individual completa por ID.

    Args:
        news_id: ID da notícia no Typesense

    Returns:
        Dicionário com dados completos da notícia
    """
    client = get_typesense_client()

    try:
        document = client.get_document("news", news_id)

        if not document:
            return {
                "error": f"Notícia com ID '{news_id}' não encontrada",
                "id": news_id
            }

        return document

    except Exception as e:
        logger.error(f"Failed to get news by ID {news_id}: {e}")
        return {
            "error": f"Erro ao buscar notícia: {str(e)}",
            "id": news_id
        }


def format_news(news: dict[str, Any]) -> str:
    """
    Formata notícia individual em Markdown.

    Args:
        news: Dicionário com dados da notícia

    Returns:
        String formatada em Markdown
    """
    if "error" in news:
        return f"# Erro\n\n{news['error']}"

    lines = []

    # Título
    title = news.get("title", "Sem título")
    lines.append(f"# {title}\n")

    # Metadados
    lines.append("## Metadados\n")

    agency = news.get("agency", "N/A")
    lines.append(f"**Agência:** {agency}")

    published_at = news.get("published_at")
    if published_at:
        published_formatted = format_timestamp(published_at)
        lines.append(f"**Data de publicação:** {published_formatted}")

    year = news.get("year")
    if year:
        lines.append(f"**Ano:** {year}")

    category = news.get("category", "N/A")
    if category and category != "N/A":
        lines.append(f"**Categoria:** {category}")

    theme = news.get("theme", "N/A")
    if theme and theme != "N/A":
        lines.append(f"**Tema:** {theme}")

    url = news.get("url")
    if url:
        lines.append(f"**URL:** {url}")

    doc_id = news.get("id")
    if doc_id:
        lines.append(f"**ID:** `{doc_id}`")

    lines.append("")

    # Conteúdo
    content = news.get("content", "Conteúdo não disponível")
    lines.append("## Conteúdo\n")
    lines.append(content)

    return "\n".join(lines)
