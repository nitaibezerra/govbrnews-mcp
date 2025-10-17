"""
Resource para lista de agências do dataset GovBRNews.
"""

import logging
from typing import Any

from ..typesense_client import get_typesense_client

logger = logging.getLogger(__name__)


def get_agencies() -> dict[str, Any]:
    """
    Obtém lista completa de agências com contagens.

    Returns:
        Dicionário com lista de agências e contagens
    """
    client = get_typesense_client()

    agencies = []
    try:
        # Usar facets para obter todas as agências
        facet_result = client.client.collections["news"].documents.search({
            "q": "*",
            "query_by": "title",
            "facet_by": "agency",
            "per_page": 0,
            "max_facet_values": 200  # Limite alto para pegar todas
        })

        if "facet_counts" in facet_result:
            for facet in facet_result["facet_counts"]:
                if facet["field_name"] == "agency":
                    agencies = [
                        {
                            "agency": count["value"],
                            "count": count["count"]
                        }
                        for count in facet["counts"]
                    ]
                    # Já vem ordenado por contagem decrescente
                    break
    except Exception as e:
        logger.error(f"Failed to get agencies: {e}")
        return {
            "error": "Não foi possível obter lista de agências",
            "agencies": []
        }

    return {
        "total_agencies": len(agencies),
        "agencies": agencies
    }


def format_agencies(agencies_data: dict[str, Any]) -> str:
    """
    Formata lista de agências em Markdown.

    Args:
        agencies_data: Dicionário com dados das agências

    Returns:
        String formatada em Markdown
    """
    if "error" in agencies_data:
        return f"# Erro\n\n{agencies_data['error']}"

    lines = ["# Agências Governamentais\n"]

    total = agencies_data.get("total_agencies", 0)
    lines.append(f"**Total de agências:** {total}\n")

    agencies = agencies_data.get("agencies", [])
    if agencies:
        lines.append("## Lista de Agências (ordenado por quantidade)\n")

        for agency_info in agencies:
            agency = agency_info["agency"]
            count = agency_info["count"]
            lines.append(f"- **{agency}:** {count:,} notícias")

    return "\n".join(lines)
