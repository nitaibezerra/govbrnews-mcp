"""FastMCP server for GovBRNews."""

import logging
from mcp.server.fastmcp import FastMCP

from .tools.search import search_news
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

logger.info("Registered tools: search_news")


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
