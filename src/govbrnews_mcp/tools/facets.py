"""
Tool para obter agregações e estatísticas do dataset GovBRNews.
"""

import logging
from typing import Any

from ..typesense_client import get_typesense_client
from ..utils.formatters import format_facets_results

logger = logging.getLogger(__name__)


def get_facets(
    facet_fields: list[str],
    query: str = "*",
    max_values: int = 20
) -> str:
    """
    Obtém agregações e estatísticas por campos específicos.

    Esta ferramenta permite análises agregadas do dataset, como:
    - Quantas notícias cada agência publicou
    - Distribuição de notícias por tema
    - Volume de publicações por ano
    - Categorias mais comuns

    Args:
        facet_fields: Lista de campos para agregar. Valores válidos:
                      - "agency": Agências governamentais
                      - "published_year": Ano de publicação
                      - "theme_1_level_1": Tema principal
                      - "category": Categoria da notícia
        query: Query opcional para filtrar resultados (padrão: "*" para todos)
        max_values: Máximo de valores por facet (1-100, padrão: 20)

    Returns:
        String formatada em Markdown com as agregações

    Examples:
        >>> get_facets(["agency"], query="educação")
        # Retorna contagem de notícias sobre educação por agência

        >>> get_facets(["published_year", "agency"], max_values=5)
        # Retorna top 5 anos e top 5 agências

        >>> get_facets(["theme_1_level_1"], query="saúde")
        # Retorna temas relacionados a saúde
    """
    # Validar facet_fields
    valid_fields = {"agency", "published_year", "theme_1_level_1", "category"}
    invalid_fields = set(facet_fields) - valid_fields

    if invalid_fields:
        return f"""# Erro

Campos inválidos: {', '.join(invalid_fields)}

**Campos válidos:**
- `agency` - Agências governamentais
- `published_year` - Ano de publicação
- `theme_1_level_1` - Tema principal
- `category` - Categoria da notícia"""

    # Validar max_values
    if not 1 <= max_values <= 100:
        max_values = min(max(1, max_values), 100)
        logger.warning(f"max_values ajustado para {max_values}")

    if not facet_fields:
        return """# Erro

Nenhum campo de facet especificado. Forneça ao menos um campo válido."""

    client = get_typesense_client()

    try:
        # Preparar query Typesense
        facet_by = ",".join(facet_fields)

        logger.info(f"Executing facets query: fields={facet_fields}, query='{query}', max={max_values}")

        results = client.client.collections["news"].documents.search({
            "q": query,
            "query_by": "title,content",
            "facet_by": facet_by,
            "per_page": 0,  # Não precisamos dos documentos
            "max_facet_values": max_values
        })

        if "facet_counts" not in results or not results["facet_counts"]:
            return f"""# Agregações

**Query:** `{query}`
**Campos:** {', '.join(facet_fields)}

Nenhuma agregação encontrada."""

        # Formatar resultados
        formatted = format_facets_results(results, query)
        return formatted

    except Exception as e:
        logger.error(f"Error getting facets: {e}", exc_info=True)
        return f"""# Erro ao Obter Agregações

**Erro:** {str(e)}

**Query:** `{query}`
**Campos solicitados:** {', '.join(facet_fields)}

Verifique se os campos são válidos e tente novamente."""
