"""
Tool para encontrar notícias similares do dataset GovBRNews.
"""

import logging
from typing import Any

from ..typesense_client import get_typesense_client
from ..utils.formatters import format_search_results

logger = logging.getLogger(__name__)


def similar_news(
    reference_id: str,
    limit: int = 5
) -> str:
    """
    Encontra notícias similares a uma notícia de referência.

    A similaridade é determinada por:
    1. Mesma agência governamental
    2. Mesmo tema principal
    3. Período temporal próximo

    Args:
        reference_id: ID da notícia de referência no Typesense
        limit: Máximo de notícias similares a retornar (1-20, padrão: 5)

    Returns:
        String formatada em Markdown com notícias similares

    Examples:
        >>> similar_news("254647")
        # Retorna 5 notícias similares à notícia 254647

        >>> similar_news("254647", limit=10)
        # Retorna 10 notícias similares
    """
    # Validar limit
    if not 1 <= limit <= 20:
        limit = min(max(1, limit), 20)
        logger.warning(f"limit ajustado para {limit}")

    client = get_typesense_client()

    try:
        # 1. Buscar notícia de referência
        logger.info(f"Fetching reference document: {reference_id}")

        try:
            reference_doc = client.get_document("news", reference_id)
        except Exception as e:
            logger.error(f"Failed to get reference document {reference_id}: {e}")
            return f"""# Erro

Notícia com ID `{reference_id}` não encontrada.

Verifique se o ID está correto e tente novamente."""

        # 2. Extrair características para similaridade
        agency = reference_doc.get("agency")
        theme = reference_doc.get("theme_1_level_1")
        year = reference_doc.get("published_year")
        title = reference_doc.get("title", "")

        logger.info(f"Reference doc: agency={agency}, theme={theme}, year={year}")

        # 3. Construir query de similaridade
        # Prioridade: mesmo tema e agência > mesmo tema > mesma agência
        filter_parts = []

        if agency:
            filter_parts.append(f"agency:={agency}")

        if theme:
            filter_parts.append(f"theme_1_level_1:={theme}")

        # Se não tiver filtros, usa período temporal
        if not filter_parts and year:
            # Busca no mesmo ano ou próximo
            year_range = f"published_year:>={year - 1} && published_year:<={year + 1}"
            filter_parts.append(year_range)

        filter_query = " && ".join(filter_parts) if filter_parts else None

        # 4. Buscar notícias similares
        search_params: dict[str, Any] = {
            "q": "*",
            "query_by": "title,content",
            "per_page": limit + 1,  # +1 para excluir a própria notícia
            "sort_by": "published_at:desc"
        }

        if filter_query:
            search_params["filter_by"] = filter_query

        logger.info(f"Searching similar news with filter: {filter_query}")

        results = client.search("news", search_params)

        # 5. Filtrar a própria notícia de referência
        hits = results.get("hits", [])
        similar_hits = [
            hit for hit in hits
            if hit["document"].get("id") != reference_id
        ][:limit]

        if not similar_hits:
            return f"""# Notícias Similares

**Notícia de referência:** {title[:80]}...
**ID:** `{reference_id}`

Nenhuma notícia similar encontrada com os critérios:
- Agência: {agency or 'N/A'}
- Tema: {theme or 'N/A'}
- Ano: {year or 'N/A'}"""

        # 6. Formatar resultados
        similar_results = {
            "found": len(similar_hits),
            "hits": similar_hits
        }

        formatted = format_search_results(similar_results)

        # Adicionar cabeçalho com informações da referência
        header = f"""# Notícias Similares

**Notícia de referência:** {title[:80]}...
**ID:** `{reference_id}`
**Agência:** {agency or 'N/A'}
**Tema:** {theme or 'N/A'}
**Ano:** {year or 'N/A'}

**Critério de similaridade:** Mesma agência e/ou tema
**Encontrado:** {len(similar_hits)} notícias similares

---

"""
        return header + formatted

    except Exception as e:
        logger.error(f"Error finding similar news: {e}", exc_info=True)
        return f"""# Erro ao Buscar Notícias Similares

**Erro:** {str(e)}

**ID de referência:** `{reference_id}`

Ocorreu um erro ao buscar notícias similares. Tente novamente."""
