"""FastMCP server for GovBRNews."""

import logging
from mcp.server.fastmcp import FastMCP

from .tools import search_news, get_facets, similar_news, analyze_temporal
from .resources import (
    get_stats,
    format_stats,
    get_agencies,
    format_agencies,
    get_themes,
    format_themes,
    get_news_by_id,
    format_news,
)
from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="GovBRNews",
)

logger.info("Initializing GovBRNews MCP Server")

# Register tools using FastMCP decorators
mcp.tool()(search_news)
mcp.tool()(get_facets)
mcp.tool()(similar_news)
mcp.tool()(analyze_temporal)

logger.info("Registered tools: search_news, get_facets, similar_news, analyze_temporal")

# Register resources using FastMCP decorators
@mcp.resource("govbrnews://stats")
def stats_resource() -> str:
    """Estatísticas gerais do dataset GovBRNews."""
    stats = get_stats()
    return format_stats(stats)


@mcp.resource("govbrnews://agencies")
def agencies_resource() -> str:
    """Lista completa de agências governamentais com contagens."""
    agencies = get_agencies()
    return format_agencies(agencies)


@mcp.resource("govbrnews://themes")
def themes_resource() -> str:
    """Taxonomia completa de temas com contagens."""
    themes = get_themes()
    return format_themes(themes)


@mcp.resource("govbrnews://news/{news_id}")
def news_resource(news_id: str) -> str:
    """
    Notícia individual completa.

    Args:
        news_id: ID da notícia no Typesense
    """
    news = get_news_by_id(news_id)
    return format_news(news)


logger.info("Registered resources: stats, agencies, themes, news/{id}")


# Register prompts using FastMCP decorators
@mcp.prompt()
def analyze_theme(theme: str) -> list[dict]:
    """
    Análise completa de um tema específico no dataset GovBRNews.

    Este prompt guia uma análise abrangente de um tema, incluindo:
    - Volume de publicações e distribuição temporal
    - Principais agências que publicam sobre o tema
    - Temas relacionados e categorias
    - Notícias mais relevantes
    - Insights e padrões identificados

    Args:
        theme: Tema a ser analisado (ex: "educação", "saúde", "meio ambiente")

    Returns:
        Lista de mensagens para análise completa do tema

    Examples:
        >>> analyze_theme("educação")
        >>> analyze_theme("meio ambiente")
        >>> analyze_theme("segurança pública")
    """
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""Realize uma análise completa e detalhada sobre o tema: **{theme}**

Siga este roteiro de análise:

## 1. Visão Geral
- Use `search_news` para obter volume total de notícias sobre "{theme}"
- Use `analyze_temporal` com granularidade mensal para mostrar evolução nos últimos 12-24 meses
- Identifique tendências: crescimento, queda, sazonalidade

## 2. Análise por Agências
- Use `get_facets` com campo "agency" para identificar top 10 agências que mais publicam sobre "{theme}"
- Analise a distribuição: há concentração ou diversidade?
- Destaque agências principais e seus volumes

## 3. Análise Temática
- Use `get_facets` com campo "theme_1_level_1" para identificar temas relacionados
- Mostre quais sub-temas ou temas correlatos são mais frequentes
- Identifique conexões interessantes

## 4. Análise Temporal Detalhada
- Use `analyze_temporal` com granularidade semanal para últimas 8 semanas
- Identifique picos recentes e possíveis causas
- Compare com mesmo período do ano anterior (se aplicável)

## 5. Notícias Mais Relevantes
- Use `search_news` para obter top 5 notícias mais relevantes sobre "{theme}"
- Ordene por relevância
- Resuma principais manchetes e insights

## 6. Síntese e Insights
- Resuma os principais achados
- Identifique padrões interessantes
- Sugira possíveis análises de aprofundamento
- Contextualize os dados (se houver conhecimento sobre eventos relevantes)

**Importante:** Use todos os tools disponíveis para criar uma análise rica e multifacetada."""
            }
        }
    ]


@mcp.prompt()
def compare_agencies(agencies: list[str], theme: str = "*") -> list[dict]:
    """
    Comparação detalhada entre múltiplas agências governamentais.

    Este prompt guia uma análise comparativa entre 2 ou mais agências,
    incluindo volumes, temas, temporalidade e diferenças de cobertura.

    Args:
        agencies: Lista de agências a comparar (ex: ["MEC", "MMA", "MS"])
        theme: Tema específico para comparação (opcional, padrão: todas as notícias)

    Returns:
        Lista de mensagens para comparação detalhada de agências

    Examples:
        >>> compare_agencies(["MEC", "INEP"])
        >>> compare_agencies(["MMA", "IBAMA", "ICMBio"], theme="meio ambiente")
        >>> compare_agencies(["MS", "ANVISA"], theme="saúde pública")
    """
    agencies_str = ", ".join(agencies)
    theme_filter = f" sobre **{theme}**" if theme != "*" else ""

    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""Realize uma comparação detalhada entre as agências: **{agencies_str}**{theme_filter}

Siga este roteiro de análise comparativa:

## 1. Volumes Globais
Para cada agência ({agencies_str}):
- Use `search_news` com filtro de agency para obter volume total{theme_filter}
- Compare os volumes absolutos
- Calcule percentuais relativos

## 2. Distribuição Temporal
- Use `analyze_temporal` (granularidade mensal, últimos 12 meses) para CADA agência separadamente
- Compare as evoluções temporais
- Identifique padrões divergentes ou convergentes
- Há períodos onde uma agência aumenta e outra diminui?

## 3. Distribuição Temática
- Use `get_facets` com campo "theme_1_level_1" para CADA agência
- Compare os temas que cada agência mais aborda
- Identifique especializações e sobreposições
- Quais temas são exclusivos de cada agência?

## 4. Análise Recente (Últimas 8 Semanas)
- Use `analyze_temporal` (granularidade semanal) para CADA agência
- Identifique agência mais ativa recentemente
- Compare ritmo de publicação

## 5. Categorias de Publicação
- Use `get_facets` com campo "category" para CADA agência
- Compare tipos de publicação (notícias, artigos, releases, etc)
- Identifique diferenças de estilo/formato

## 6. Notícias Representativas
- Use `search_news` para obter 3 notícias mais relevantes de CADA agência{theme_filter}
- Mostre exemplos concretos de cobertura de cada agência
- Identifique diferenças de abordagem

## 7. Síntese Comparativa
- Resuma semelhanças e diferenças
- Identifique especializações de cada agência
- Sugira possíveis razões para diferenças observadas
- Recomende análises de aprofundamento

**Importante:** Faça análises paralelas para permitir comparação direta entre agências."""
            }
        }
    ]


@mcp.prompt()
def temporal_evolution(
    query: str,
    year_from: int | None = None,
    year_to: int | None = None
) -> list[dict]:
    """
    Análise de evolução temporal de um tema com múltiplas granularidades.

    Este prompt guia uma análise temporal profunda combinando visões
    de longo prazo (anual) e curto prazo (mensal/semanal).

    Args:
        query: Termo de busca para análise temporal
        year_from: Ano inicial da análise (opcional)
        year_to: Ano final da análise (opcional)

    Returns:
        Lista de mensagens para análise temporal detalhada

    Examples:
        >>> temporal_evolution("educação", 2020, 2025)
        >>> temporal_evolution("COP30")
        >>> temporal_evolution("segurança pública", year_from=2023)
    """
    years_filter = ""
    if year_from and year_to:
        years_filter = f" entre **{year_from}** e **{year_to}**"
    elif year_from:
        years_filter = f" desde **{year_from}**"
    elif year_to:
        years_filter = f" até **{year_to}**"

    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""Realize uma análise temporal completa sobre: **{query}**{years_filter}

Siga este roteiro de análise temporal em múltiplas escalas:

## 1. Tendência de Longo Prazo (Anual)
- Use `analyze_temporal` com granularidade **yearly**{years_filter if years_filter else " (todos os anos disponíveis)"}
- Identifique tendência geral: crescimento, estabilidade ou queda
- Calcule taxa de crescimento anual
- Identifique anos de pico e vale
- Contextualize com possíveis eventos (se conhecidos)

## 2. Padrões de Médio Prazo (Mensal)
- Use `analyze_temporal` com granularidade **monthly** para últimos 24 meses
- Identifique sazonalidade: há meses com mais/menos publicações?
- Compare mesmo mês em anos diferentes
- Identifique mudanças de ritmo ao longo do ano

## 3. Dinâmica Recente (Semanal)
- Use `analyze_temporal` com granularidade **weekly** para últimas 12 semanas
- Identifique picos e vales recentes
- Compare com média histórica
- Detecte eventos ou mudanças súbitas

## 4. Análise de Agências ao Longo do Tempo
- Use `get_facets` com campo "agency" para identificar top 5 agências
- Para cada top agência, analise evolução temporal separadamente
- Identifique mudanças na composição: agências que aumentaram/diminuíram relevância

## 5. Evolução Temática
- Use `get_facets` com campo "theme_1_level_1"
- Compare distribuição temática em períodos diferentes
- Identifique temas emergentes vs temas em declínio
- Use `search_news` com filtros temporais para comparar períodos

## 6. Análise de Momentos Críticos
- Identifique os 3 períodos de maior volume
- Identifique os 3 períodos de menor volume
- Para cada momento crítico, use `search_news` para obter notícias representativas
- Tente identificar causas dos picos/vales

## 7. Projeção e Tendências
- Com base nos dados históricos, qual a tendência?
- Há sinais de aceleração ou desaceleração?
- Que eventos futuros podem impactar o tema?

## 8. Síntese Temporal
- Resuma a narrativa temporal completa
- Destaque inflexões importantes
- Identifique padrões cíclicos ou únicos
- Sugira hipóteses para variações observadas

**Importante:** Combine as três granularidades (yearly, monthly, weekly) para construir uma visão temporal completa e multi-escala."""
            }
        }
    ]


@mcp.prompt()
def discover_context(news_id: str) -> list[dict]:
    """
    Descoberta do contexto completo em torno de uma notícia específica.

    Este prompt guia uma investigação contextual profunda de uma notícia,
    incluindo notícias relacionadas, histórico do tema, e panorama temporal.

    Args:
        news_id: ID da notícia no Typesense

    Returns:
        Lista de mensagens para descoberta contextual completa

    Examples:
        >>> discover_context("abc123")
        >>> discover_context("news_2025_10_23_001")
    """
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""Realize uma investigação contextual completa sobre a notícia com ID: **{news_id}**

Siga este roteiro de descoberta contextual:

## 1. Notícia de Referência
- Use resource `govbrnews://news/{news_id}` para obter dados completos da notícia
- Extraia: título, agência, data, tema principal, conteúdo
- Resuma a notícia de referência

## 2. Notícias Similares
- Use `similar_news` com ID da notícia de referência
- Analise as 5-10 notícias mais similares
- Identifique: mesma agência? mesmo tema? mesmo período?
- Há uma narrativa conectando essas notícias?

## 3. Contexto Temporal
- Com base na data da notícia, use `search_news` para buscar notícias sobre o mesmo tema:
  - 1 semana antes da publicação
  - Na mesma semana
  - 1 semana depois
- Monte uma linha do tempo contextual

## 4. Contexto Temático Amplo
- Use o tema principal da notícia
- Use `analyze_temporal` (monthly) para entender evolução do tema nos últimos 6 meses
- A notícia ocorre em período de pico ou vale?
- Use `get_facets` para entender landscape temático

## 5. Contexto da Agência
- Use `search_news` com filtro da agência da notícia
- Busque outras notícias recentes da mesma agência (últimas 2 semanas)
- Identifique prioridades recentes da agência
- A notícia faz parte de uma campanha/série?

## 6. Reações e Desdobramentos
- Use `search_news` com termos-chave da notícia original
- Filtre por datas APÓS a publicação
- Identifique notícias que podem ser desdobramentos ou reações
- Houve cobertura subsequente?

## 7. Contexto Histórico
- Use `search_news` com termos-chave para buscar no arquivo histórico
- Identifique primeira menção ao tema
- Identifique marcos importantes relacionados
- Monte histórico resumido

## 8. Síntese Contextual
- Resuma o contexto completo da notícia:
  - Por que foi publicada neste momento?
  - Qual o contexto temático mais amplo?
  - Há uma narrativa maior em jogo?
  - Qual a relevância desta notícia no panorama geral?

**Importante:** Use todos os tools e resources disponíveis para construir contexto rico e multidimensional."""
            }
        }
    ]


logger.info("Registered prompts: analyze_theme, compare_agencies, temporal_evolution, discover_context")


def main():
    """Entry point for the MCP server."""
    logger.info("Starting GovBRNews MCP Server...")
    logger.info(f"Typesense endpoint: {settings.typesense_protocol}://"
                f"{settings.typesense_host}:{settings.typesense_port}")

    try:
        # Run the FastMCP server
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
