"""Typesense client wrapper for GovBRNews MCP Server."""

import logging
from typing import Any

import typesense
from typesense.exceptions import ObjectNotFound, RequestUnauthorized, TypesenseClientError

from .config import settings

logger = logging.getLogger(__name__)


class TypesenseClient:
    """Wrapper around Typesense client with error handling."""

    def __init__(self):
        """Initialize Typesense client."""
        self.client = typesense.Client(
            {
                "nodes": [
                    {
                        "host": settings.typesense_host,
                        "port": str(settings.typesense_port),
                        "protocol": settings.typesense_protocol,
                    }
                ],
                "api_key": settings.typesense_api_key,
                "connection_timeout_seconds": 10,
            }
        )
        logger.info(
            f"Typesense client initialized: {settings.typesense_protocol}://"
            f"{settings.typesense_host}:{settings.typesense_port}"
        )

    def search(self, collection: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Execute search query on a collection.

        Args:
            collection: Collection name to search
            params: Search parameters (query, filters, etc.)

        Returns:
            Search results dictionary

        Raises:
            TypesenseClientError: If search fails
        """
        try:
            logger.debug(f"Searching collection '{collection}' with params: {params}")
            results = self.client.collections[collection].documents.search(params)
            logger.debug(f"Search returned {results.get('found', 0)} results")
            return results

        except ObjectNotFound as e:
            logger.error(f"Collection '{collection}' not found: {e}")
            raise

        except RequestUnauthorized as e:
            logger.error(f"Unauthorized access to Typesense: {e}")
            raise

        except TypesenseClientError as e:
            logger.error(f"Typesense search error: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise

    def get_collection_info(self, collection: str) -> dict[str, Any]:
        """
        Get collection metadata.

        Args:
            collection: Collection name

        Returns:
            Collection information dictionary

        Raises:
            TypesenseClientError: If retrieval fails
        """
        try:
            logger.debug(f"Getting info for collection '{collection}'")
            info = self.client.collections[collection].retrieve()
            return info

        except ObjectNotFound as e:
            logger.error(f"Collection '{collection}' not found: {e}")
            raise

        except TypesenseClientError as e:
            logger.error(f"Error retrieving collection info: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error getting collection info: {e}")
            raise

    def get_document(self, collection: str, document_id: str) -> dict[str, Any]:
        """
        Retrieve a single document by ID.

        Args:
            collection: Collection name
            document_id: Document unique ID

        Returns:
            Document dictionary

        Raises:
            ObjectNotFound: If document doesn't exist
            TypesenseClientError: If retrieval fails
        """
        try:
            logger.debug(f"Getting document '{document_id}' from '{collection}'")
            doc = self.client.collections[collection].documents[document_id].retrieve()
            return doc

        except ObjectNotFound:
            logger.warning(f"Document '{document_id}' not found in '{collection}'")
            raise

        except TypesenseClientError as e:
            logger.error(f"Error retrieving document: {e}")
            raise

    def health_check(self) -> bool:
        """
        Check if Typesense server is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            health = self.client.operations.health()
            is_healthy = health.get("ok", False)
            logger.debug(f"Health check: {'OK' if is_healthy else 'FAILED'}")
            return is_healthy

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Singleton instance
typesense_client = TypesenseClient()
