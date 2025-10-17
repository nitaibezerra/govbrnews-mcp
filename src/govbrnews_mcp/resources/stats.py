"""
Resource para estatísticas gerais do dataset GovBRNews.
"""

import logging
from typing import Any

from ..typesense_client import get_typesense_client
from ..utils.formatters import format_timestamp

logger = logging.getLogger(__name__)


def get_stats() -> dict[str, Any]:
    """
    Obtém estatísticas gerais do dataset.

    Returns:
        Dicionário com estatísticas do dataset
    """
    client = get_typesense_client()

    # Obter informações da coleção
    collection_info = client.get_collection_info("news")

    if not collection_info:
        logger.error("Failed to get collection info")
        return {
            "error": "Não foi possível obter estatísticas do dataset",
            "total_documents": 0
        }

    total_docs = collection_info.get("num_documents", 0)

    # Buscar distribuição por ano (últimos 10 anos visíveis)
    year_distribution = {}
    try:
        # Usar facets para obter distribuição por ano
        facet_result = client.client.collections["news"].documents.search({
            "q": "*",
            "query_by": "title",
            "facet_by": "published_year",
            "per_page": 0,
            "max_facet_values": 20
        })

        if "facet_counts" in facet_result:
            for facet in facet_result["facet_counts"]:
                if facet["field_name"] == "published_year":
                    for count in facet["counts"]:
                        year_distribution[count["value"]] = count["count"]
    except Exception as e:
        logger.warning(f"Failed to get year distribution: {e}")
        year_distribution = {}

    # Buscar top 5 agências
    top_agencies = []
    try:
        facet_result = client.client.collections["news"].documents.search({
            "q": "*",
            "query_by": "title",
            "facet_by": "agency",
            "per_page": 0,
            "max_facet_values": 5
        })

        if "facet_counts" in facet_result:
            for facet in facet_result["facet_counts"]:
                if facet["field_name"] == "agency":
                    top_agencies = [
                        {"agency": count["value"], "count": count["count"]}
                        for count in facet["counts"][:5]
                    ]
    except Exception as e:
        logger.warning(f"Failed to get top agencies: {e}")
        top_agencies = []

    # Buscar período de cobertura
    coverage_period = {}
    try:
        # Buscar notícia mais antiga
        oldest_result = client.search("news", {
            "q": "*",
            "query_by": "title",
            "sort_by": "published_at:asc",
            "per_page": 1
        })

        # Buscar notícia mais recente
        newest_result = client.search("news", {
            "q": "*",
            "query_by": "title",
            "sort_by": "published_at:desc",
            "per_page": 1
        })

        if oldest_result.get("found", 0) > 0:
            oldest_doc = oldest_result["hits"][0]["document"]
            coverage_period["start_date"] = oldest_doc.get("published_at")
            coverage_period["start_date_formatted"] = format_timestamp(
                oldest_doc.get("published_at")
            )

        if newest_result.get("found", 0) > 0:
            newest_doc = newest_result["hits"][0]["document"]
            coverage_period["end_date"] = newest_doc.get("published_at")
            coverage_period["end_date_formatted"] = format_timestamp(
                newest_doc.get("published_at")
            )
    except Exception as e:
        logger.warning(f"Failed to get coverage period: {e}")
        coverage_period = {}

    return {
        "total_documents": total_docs,
        "year_distribution": year_distribution,
        "top_agencies": top_agencies,
        "coverage_period": coverage_period
    }


def format_stats(stats: dict[str, Any]) -> str:
    """
    Formata estatísticas em Markdown.

    Args:
        stats: Dicionário com estatísticas

    Returns:
        String formatada em Markdown
    """
    if "error" in stats:
        return f"# Erro\n\n{stats['error']}"

    lines = ["# Estatísticas do Dataset GovBRNews\n"]

    # Total de documentos
    total = stats.get("total_documents", 0)
    lines.append(f"**Total de documentos:** {total:,} notícias\n")

    # Período de cobertura
    coverage = stats.get("coverage_period", {})
    if coverage:
        start = coverage.get("start_date_formatted", "N/A")
        end = coverage.get("end_date_formatted", "N/A")
        lines.append(f"**Período de cobertura:** {start} até {end}\n")

    # Distribuição por ano
    year_dist = stats.get("year_distribution", {})
    if year_dist:
        lines.append("## Distribuição por Ano\n")
        # Ordenar por ano decrescente
        sorted_years = sorted(year_dist.items(), key=lambda x: x[0], reverse=True)
        for year, count in sorted_years[:10]:  # Top 10 anos
            lines.append(f"- **{year}:** {count:,} notícias")
        lines.append("")

    # Top agências
    top_agencies = stats.get("top_agencies", [])
    if top_agencies:
        lines.append("## Top 5 Agências\n")
        for i, agency_info in enumerate(top_agencies, 1):
            agency = agency_info["agency"]
            count = agency_info["count"]
            lines.append(f"{i}. **{agency}:** {count:,} notícias")
        lines.append("")

    return "\n".join(lines)
