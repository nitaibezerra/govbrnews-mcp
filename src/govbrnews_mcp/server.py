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
