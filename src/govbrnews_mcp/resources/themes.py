"""
Resource para taxonomia de temas do dataset GovBRNews.
"""

import logging
from typing import Any

from ..typesense_client import get_typesense_client

logger = logging.getLogger(__name__)


def get_themes() -> dict[str, Any]:
    """
    Obtém taxonomia completa de temas com contagens.

    Returns:
        Dicionário com lista de temas e contagens
    """
    client = get_typesense_client()

    themes = []
    try:
        # Usar facets para obter todos os temas
        facet_result = client.client.collections["news"].documents.search({
            "q": "*",
            "query_by": "title",
            "facet_by": "theme_1_level_1",
            "per_page": 0,
            "max_facet_values": 100  # Limite alto para pegar todos
        })

        if "facet_counts" in facet_result:
            for facet in facet_result["facet_counts"]:
                if facet["field_name"] == "theme_1_level_1":
                    themes = [
                        {
                            "theme": count["value"],
                            "count": count["count"]
                        }
                        for count in facet["counts"]
                    ]
                    # Já vem ordenado por contagem decrescente
                    break
    except Exception as e:
        logger.error(f"Failed to get themes: {e}")
        return {
            "error": "Não foi possível obter taxonomia de temas",
            "themes": []
        }

    return {
        "total_themes": len(themes),
        "themes": themes
    }


def format_themes(themes_data: dict[str, Any]) -> str:
    """
    Formata taxonomia de temas em Markdown.

    Args:
        themes_data: Dicionário com dados dos temas

    Returns:
        String formatada em Markdown
    """
    if "error" in themes_data:
        return f"# Erro\n\n{themes_data['error']}"

    lines = ["# Taxonomia de Temas\n"]

    total = themes_data.get("total_themes", 0)
    lines.append(f"**Total de temas:** {total}\n")

    themes = themes_data.get("themes", [])
    if themes:
        lines.append("## Lista de Temas (ordenado por quantidade)\n")

        for theme_info in themes:
            theme = theme_info["theme"]
            count = theme_info["count"]
            lines.append(f"- **{theme}:** {count:,} notícias")

    return "\n".join(lines)
