"""
Tool para análise temporal de notícias com diferentes granularidades.
"""

import logging

from ..utils.temporal import get_temporal_distribution, format_temporal_distribution

logger = logging.getLogger(__name__)


def analyze_temporal(
    query: str,
    granularity: str = "monthly",
    year_from: int | None = None,
    year_to: int | None = None,
    max_periods: int = 24
) -> str:
    """
    Analisa distribuição temporal de notícias com granularidade configurável.

    Esta ferramenta permite análises temporais detalhadas:
    - **Anual (yearly)**: Distribuição por ano
    - **Mensal (monthly)**: Distribuição por mês [RECOMENDADO]
    - **Semanal (weekly)**: Distribuição por semana (máx 52 semanas/1 ano)

    Args:
        query: Termo de busca para filtrar notícias
        granularity: Granularidade temporal:
                     - "yearly": Distribuição anual
                     - "monthly": Distribuição mensal (padrão)
                     - "weekly": Distribuição semanal
        year_from: Filtrar a partir deste ano (opcional)
        year_to: Filtrar até este ano (opcional)
        max_periods: Máximo de períodos para retornar (padrão: 24)
                     - yearly: máx 50 anos
                     - monthly: máx 60 meses (5 anos)
                     - weekly: máx 52 semanas (1 ano)

    Returns:
        String formatada em Markdown com distribuição temporal e estatísticas

    Examples:
        >>> analyze_temporal("educação", "monthly", 2024, 2025)
        # Distribuição mensal de notícias sobre educação em 2024-2025

        >>> analyze_temporal("saúde", "weekly", max_periods=12)
        # Últimas 12 semanas de notícias sobre saúde

        >>> analyze_temporal("meio ambiente", "yearly")
        # Distribuição anual de notícias sobre meio ambiente

    Notes:
        - Granularidade MENSAL é a mais recomendada (balance entre detalhe e performance)
        - Granularidade SEMANAL limitada a 52 semanas (1 ano) por performance
        - Use year_from/year_to para focar em períodos específicos
    """
    try:
        # Validar granularity
        if granularity not in ["yearly", "monthly", "weekly"]:
            return f"""# Erro

Granularidade inválida: `{granularity}`

**Granularidades válidas:**
- `yearly` - Distribuição anual
- `monthly` - Distribuição mensal (recomendado)
- `weekly` - Distribuição semanal (máx 52 semanas)"""

        # Validar max_periods por granularidade
        if granularity == "yearly" and max_periods > 50:
            max_periods = 50
        elif granularity == "monthly" and max_periods > 60:
            max_periods = 60
        elif granularity == "weekly" and max_periods > 52:
            max_periods = 52

        logger.info(
            f"Analyzing temporal distribution: query='{query}', "
            f"granularity={granularity}, year_from={year_from}, "
            f"year_to={year_to}, max_periods={max_periods}"
        )

        # Obter distribuição temporal
        data = get_temporal_distribution(
            query=query,
            granularity=granularity,
            year_from=year_from,
            year_to=year_to,
            max_periods=max_periods
        )

        # Formatar para exibição
        formatted = format_temporal_distribution(data)
        return formatted

    except Exception as e:
        logger.error(f"Error in temporal analysis: {e}", exc_info=True)
        return f"""# Erro na Análise Temporal

**Erro:** {str(e)}
**Query:** `{query}`
**Granularidade:** {granularity}

Tente novamente com parâmetros diferentes."""
