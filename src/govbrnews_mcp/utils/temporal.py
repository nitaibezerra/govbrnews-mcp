"""
Utilidades para análise temporal com diferentes granularidades.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..typesense_client import get_typesense_client

logger = logging.getLogger(__name__)


def get_temporal_distribution(
    query: str = "*",
    granularity: str = "monthly",
    year_from: int | None = None,
    year_to: int | None = None,
    max_periods: int = 24
) -> dict[str, Any]:
    """
    Obtém distribuição temporal de notícias com granularidade configurável.

    Args:
        query: Query para filtrar notícias (padrão: "*" para todas)
        granularity: Granularidade temporal:
                     - "yearly": Por ano
                     - "monthly": Por mês (recomendado)
                     - "weekly": Por semana (limitado a max_periods semanas)
        year_from: Ano inicial do filtro (opcional)
        year_to: Ano final do filtro (opcional)
        max_periods: Máximo de períodos para retornar (padrão: 24)

    Returns:
        Dicionário com distribuição temporal e metadados

    Examples:
        >>> get_temporal_distribution("educação", "monthly", 2024, 2025)
        # Retorna distribuição mensal de notícias sobre educação em 2024-2025

        >>> get_temporal_distribution("saúde", "weekly", max_periods=12)
        # Retorna últimas 12 semanas de notícias sobre saúde
    """
    client = get_typesense_client()

    try:
        if granularity == "yearly":
            return _get_yearly_distribution(client, query, year_from, year_to, max_periods)
        elif granularity == "monthly":
            return _get_monthly_distribution(client, query, year_from, year_to, max_periods)
        elif granularity == "weekly":
            return _get_weekly_distribution(client, query, year_from, year_to, max_periods)
        else:
            raise ValueError(f"Granularidade inválida: {granularity}. Use 'yearly', 'monthly' ou 'weekly'")

    except Exception as e:
        logger.error(f"Error getting temporal distribution: {e}", exc_info=True)
        return {
            "error": str(e),
            "granularity": granularity,
            "query": query
        }


def _get_yearly_distribution(
    client,
    query: str,
    year_from: int | None,
    year_to: int | None,
    max_periods: int
) -> dict[str, Any]:
    """Obtém distribuição anual."""

    # Construir filtro de anos
    filter_parts = []
    if year_from:
        filter_parts.append(f"published_year:>={year_from}")
    if year_to:
        filter_parts.append(f"published_year:<={year_to}")

    filter_by = " && ".join(filter_parts) if filter_parts else None

    # Query Typesense
    search_params = {
        "q": query,
        "query_by": "title,content",
        "facet_by": "published_year",
        "per_page": 0,
        "max_facet_values": max_periods
    }

    if filter_by:
        search_params["filter_by"] = filter_by

    results = client.client.collections["news"].documents.search(search_params)

    # Processar resultados
    distribution = []
    if "facet_counts" in results:
        for facet in results["facet_counts"]:
            if facet["field_name"] == "published_year":
                for count in facet["counts"]:
                    distribution.append({
                        "period": str(count["value"]),
                        "label": str(count["value"]),
                        "count": count["count"]
                    })

    # Ordenar por período
    distribution.sort(key=lambda x: x["period"])

    return {
        "granularity": "yearly",
        "query": query,
        "total_found": results.get("found", 0),
        "distribution": distribution,
        "filters": {
            "year_from": year_from,
            "year_to": year_to
        }
    }


def _get_monthly_distribution(
    client,
    query: str,
    year_from: int | None,
    year_to: int | None,
    max_periods: int
) -> dict[str, Any]:
    """Obtém distribuição mensal."""

    # Construir filtro de anos
    filter_parts = []
    if year_from:
        filter_parts.append(f"published_year:>={year_from}")
    if year_to:
        filter_parts.append(f"published_year:<={year_to}")

    filter_by = " && ".join(filter_parts) if filter_parts else None

    # Query Typesense com facets de ano e mês
    search_params = {
        "q": query,
        "query_by": "title,content",
        "facet_by": "published_year,published_month",
        "per_page": 0,
        "max_facet_values": 50  # Máximo para capturar todos os anos e meses
    }

    if filter_by:
        search_params["filter_by"] = filter_by

    results = client.client.collections["news"].documents.search(search_params)

    # Criar mapa de contagens por ano/mês
    year_counts = {}
    month_counts = {}

    if "facet_counts" in results:
        for facet in results["facet_counts"]:
            if facet["field_name"] == "published_year":
                for count in facet["counts"]:
                    year_counts[int(count["value"])] = count["count"]
            elif facet["field_name"] == "published_month":
                for count in facet["counts"]:
                    month_counts[int(count["value"])] = count["count"]

    # Para obter contagens exatas por ano+mês, precisamos fazer queries individuais
    # Determinar range de anos
    if year_counts:
        years = sorted(year_counts.keys())
        if year_from:
            years = [y for y in years if y >= year_from]
        if year_to:
            years = [y for y in years if y <= year_to]

        # Limitar a últimos N meses se especificado
        if len(years) * 12 > max_periods:
            years = years[-(max_periods // 12 + 1):]
    else:
        # Se não há dados, usar ano atual
        current_year = datetime.now().year
        years = [current_year]

    # Buscar contagens por ano/mês
    distribution = []
    total_queries = 0

    for year in years:
        for month in range(1, 13):
            if total_queries >= max_periods:
                break

            try:
                # Query para este ano/mês específico
                month_filter = f"published_year:={year} && published_month:={month}"
                if filter_by:
                    month_filter = f"{filter_by} && published_month:={month}"

                month_results = client.client.collections["news"].documents.search({
                    "q": query,
                    "query_by": "title,content",
                    "filter_by": month_filter,
                    "per_page": 0
                })

                count = month_results.get("found", 0)

                # Só incluir meses com notícias
                if count > 0:
                    month_name = _get_month_name(month)
                    distribution.append({
                        "period": f"{year}-{month:02d}",
                        "label": f"{month_name}/{year}",
                        "year": year,
                        "month": month,
                        "count": count
                    })

                total_queries += 1

            except Exception as e:
                logger.warning(f"Error getting count for {year}-{month:02d}: {e}")
                continue

        if total_queries >= max_periods:
            break

    # Ordenar por período e limitar
    distribution.sort(key=lambda x: x["period"])
    distribution = distribution[-max_periods:]

    return {
        "granularity": "monthly",
        "query": query,
        "total_found": results.get("found", 0),
        "distribution": distribution,
        "filters": {
            "year_from": year_from,
            "year_to": year_to
        },
        "note": f"Distribuição mensal limitada a {max_periods} períodos mais recentes"
    }


def _get_weekly_distribution(
    client,
    query: str,
    year_from: int | None,
    year_to: int | None,
    max_periods: int
) -> dict[str, Any]:
    """
    Obtém distribuição semanal.

    Nota: Limitado a max_periods semanas por questões de performance.
    Recomendado: max_periods <= 26 (6 meses)
    """

    # Limitar max_periods para performance
    if max_periods > 52:
        max_periods = 52
        logger.warning(f"max_periods ajustado para 52 (1 ano) para performance")

    # Determinar range de datas
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=max_periods)

    # Ajustar por year_from/year_to se fornecido
    if year_from and start_date.year < year_from:
        start_date = datetime(year_from, 1, 1)
    if year_to and end_date.year > year_to:
        end_date = datetime(year_to, 12, 31, 23, 59, 59)

    # Construir filtro base
    filter_parts = []
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    filter_parts.append(f"published_at:>={start_timestamp}")
    filter_parts.append(f"published_at:<={end_timestamp}")

    # Gerar semanas
    distribution = []
    current = start_date
    week_num = 0

    while current < end_date and week_num < max_periods:
        week_start = current
        week_end = current + timedelta(days=7)

        if week_end > end_date:
            week_end = end_date

        try:
            # Query para esta semana
            week_filter = f"published_at:>={int(week_start.timestamp())} && published_at:<{int(week_end.timestamp())}"

            week_results = client.client.collections["news"].documents.search({
                "q": query,
                "query_by": "title,content",
                "filter_by": week_filter,
                "per_page": 0
            })

            count = week_results.get("found", 0)

            # Incluir semana mesmo se count = 0 para manter continuidade
            week_label = f"Semana de {week_start.strftime('%d/%m/%Y')}"
            distribution.append({
                "period": week_start.strftime("%Y-W%W"),
                "label": week_label,
                "start_date": week_start.isoformat(),
                "end_date": week_end.isoformat(),
                "count": count
            })

        except Exception as e:
            logger.warning(f"Error getting count for week {week_start}: {e}")

        current = week_end
        week_num += 1

    return {
        "granularity": "weekly",
        "query": query,
        "total_found": sum(d["count"] for d in distribution),
        "distribution": distribution,
        "filters": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "note": f"Distribuição semanal limitada a {max_periods} semanas. Recomendado: <= 26 semanas"
    }


def _get_month_name(month: int) -> str:
    """Retorna nome do mês em português."""
    months = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    return months[month - 1]


def format_temporal_distribution(data: dict[str, Any]) -> str:
    """
    Formata distribuição temporal para exibição em Markdown.

    Args:
        data: Dicionário retornado por get_temporal_distribution()

    Returns:
        String formatada em Markdown
    """
    if "error" in data:
        return f"""# Erro na Análise Temporal

**Erro:** {data['error']}
**Granularidade:** {data['granularity']}
**Query:** `{data['query']}`"""

    output = []
    output.append("# Distribuição Temporal")
    output.append("")
    output.append(f"**Query:** `{data['query']}`")
    output.append(f"**Granularidade:** {data['granularity']}")
    output.append(f"**Total encontrado:** {data['total_found']:,} notícias")
    output.append("")

    if "note" in data:
        output.append(f"*{data['note']}*")
        output.append("")

    # Filtros aplicados
    if data.get("filters"):
        filters = data["filters"]
        if filters.get("year_from") or filters.get("year_to"):
            output.append("**Filtros:**")
            if filters.get("year_from"):
                output.append(f"- Ano inicial: {filters['year_from']}")
            if filters.get("year_to"):
                output.append(f"- Ano final: {filters['year_to']}")
            output.append("")

    # Distribuição
    distribution = data.get("distribution", [])

    if not distribution:
        output.append("Nenhum dado encontrado para o período especificado.")
        return "\n".join(output)

    output.append("## Distribuição")
    output.append("")
    output.append("| Período | Quantidade |")
    output.append("|---------|------------|")

    for item in distribution:
        label = item.get("label", item["period"])
        count = item["count"]
        output.append(f"| {label} | {count:,} |")

    # Estatísticas resumidas
    output.append("")
    output.append("## Estatísticas")
    output.append("")

    counts = [item["count"] for item in distribution]
    if counts:
        output.append(f"- **Total de períodos:** {len(distribution)}")
        output.append(f"- **Média por período:** {sum(counts) / len(counts):.0f}")
        output.append(f"- **Máximo:** {max(counts):,} ({distribution[counts.index(max(counts))]['label']})")
        output.append(f"- **Mínimo:** {min(counts):,} ({distribution[counts.index(min(counts))]['label']})")

    return "\n".join(output)
