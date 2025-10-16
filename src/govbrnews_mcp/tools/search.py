"""Search tool for GovBRNews MCP Server."""

import logging
from typing import Literal

from ..typesense_client import typesense_client
from ..utils.formatters import format_search_results

logger = logging.getLogger(__name__)


def search_news(
    query: str,
    agencies: list[str] | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    themes: list[str] | None = None,
    limit: int = 10,
    sort: Literal["relevant", "newest", "oldest"] = "relevant",
) -> str:
    """
    Busca notícias governamentais brasileiras no dataset GovBRNews.

    Args:
        query: Termos de busca (obrigatório). Ex: "educação", "saúde pública"
        agencies: Lista de agências para filtrar. Ex: ["Ministério da Educação"]
        year_from: Ano inicial do período (2018-2025)
        year_to: Ano final do período (2018-2025)
        themes: Lista de temas para filtrar. Ex: ["Educação e Cultura"]
        limit: Número máximo de resultados (1-100, padrão: 10)
        sort: Ordenação dos resultados:
            - "relevant": Por relevância (padrão)
            - "newest": Mais recentes primeiro
            - "oldest": Mais antigos primeiro

    Returns:
        Resultados formatados em Markdown com:
        - Total de notícias encontradas
        - Lista de notícias com título, agência, data, resumo e link

    Examples:
        >>> search_news("educação", limit=5)
        >>> search_news("saúde", agencies=["Ministério da Saúde"], year_from=2024)
        >>> search_news("tecnologia", sort="newest", limit=20)
    """
    try:
        logger.info(f"Searching for: '{query}' with filters - agencies: {agencies}, "
                   f"year_from: {year_from}, year_to: {year_to}, themes: {themes}")

        # Build search parameters
        search_params = {
            "q": query,
            "query_by": "title,content",
            "per_page": min(max(limit, 1), 100),  # Clamp between 1-100
        }

        # Build filters
        filters = []

        if agencies:
            # Escape special characters and build OR filter
            escaped_agencies = [a.replace(":", "\\:") for a in agencies]
            agency_filter = " || ".join([f"agency:={a}" for a in escaped_agencies])
            filters.append(f"({agency_filter})")

        if year_from:
            filters.append(f"published_year:>={year_from}")

        if year_to:
            filters.append(f"published_year:<={year_to}")

        if themes:
            escaped_themes = [t.replace(":", "\\:") for t in themes]
            theme_filter = " || ".join([f"theme_1_level_1:={t}" for t in escaped_themes])
            filters.append(f"({theme_filter})")

        if filters:
            search_params["filter_by"] = " && ".join(filters)

        # Apply sorting
        if sort == "newest":
            search_params["sort_by"] = "published_at:desc"
        elif sort == "oldest":
            search_params["sort_by"] = "published_at:asc"
        # "relevant" uses default Typesense ranking

        # Execute search
        results = typesense_client.search("news", search_params)

        logger.info(f"Search completed: found {results.get('found', 0)} results")

        # Format results for LLM
        return format_search_results(results)

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        return (
            f"Erro ao buscar notícias: {str(e)}\n\n"
            f"Verifique se o servidor Typesense está rodando e acessível."
        )
