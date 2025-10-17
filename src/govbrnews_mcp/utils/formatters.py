"""Formatters for converting Typesense results to LLM-friendly formats."""

from datetime import datetime
from typing import Any


def format_timestamp(timestamp: int | None) -> str:
    """
    Format Unix timestamp to Brazilian date format.

    Args:
        timestamp: Unix timestamp in seconds

    Returns:
        Formatted date string (DD/MM/YYYY) or 'N/A'
    """
    if not timestamp or timestamp <= 0:
        return "N/A"

    try:
        date = datetime.fromtimestamp(timestamp)
        return date.strftime("%d/%m/%Y")
    except (ValueError, OSError):
        return "N/A"


def format_search_results(results: dict[str, Any]) -> str:
    """
    Format Typesense search results for LLM consumption.

    Args:
        results: Raw Typesense search response

    Returns:
        Markdown-formatted string with search results
    """
    found = results.get("found", 0)
    hits = results.get("hits", [])

    output = ["# Resultados da Busca\n"]
    output.append(f"**Total encontrado:** {found:,} notícias\n")
    output.append(f"**Mostrando:** {len(hits)} resultados\n\n")

    if not hits:
        output.append("*Nenhuma notícia encontrada com os critérios especificados.*\n")
        return "".join(output)

    output.append("---\n\n")

    for i, hit in enumerate(hits, 1):
        doc = hit.get("document", {})

        # Title
        title = doc.get("title", "Sem título")
        output.append(f"## {i}. {title}\n\n")

        # Metadata
        metadata = []

        if agency := doc.get("agency"):
            metadata.append(f"**Agência:** {agency}")

        if published_at := doc.get("published_at"):
            date_str = format_timestamp(published_at)
            metadata.append(f"**Publicado:** {date_str}")

        if category := doc.get("category"):
            metadata.append(f"**Categoria:** {category}")

        if theme := doc.get("theme_1_level_1"):
            metadata.append(f"**Tema:** {theme}")

        if url := doc.get("url"):
            metadata.append(f"**URL:** {url}")

        if metadata:
            output.append(" | ".join(metadata))
            output.append("\n\n")

        # Content snippet
        if content := doc.get("content"):
            snippet = content[:500].strip()
            if len(content) > 500:
                # Try to break at word boundary
                last_space = snippet.rfind(" ")
                if last_space > 400:
                    snippet = snippet[:last_space]
                snippet += "..."

            output.append(f"**Resumo:**\n{snippet}\n\n")

        output.append("---\n\n")

    return "".join(output)


def format_facets_results(results: dict[str, Any], query: str = "*") -> str:
    """
    Format faceted search results for LLM consumption.

    Args:
        results: Raw Typesense faceted search response
        query: Optional query string to display in header

    Returns:
        Markdown-formatted string with facet counts
    """
    facet_counts = results.get("facet_counts", [])

    if not facet_counts:
        return "Nenhuma agregação disponível."

    output = ["# Agregações\n\n"]

    # Add query info if not wildcard
    if query != "*":
        total_found = results.get("found", 0)
        output.append(f"**Query:** `{query}`\n")
        output.append(f"**Total encontrado:** {total_found:,} notícias\n\n")

    for facet in facet_counts:
        field_name = facet.get("field_name", "")
        counts = facet.get("counts", [])

        if not counts:
            continue

        # Translate field names to Portuguese
        field_labels = {
            "agency": "Agências",
            "category": "Categorias",
            "theme_1_level_1": "Temas",
            "published_year": "Anos",
            "published_month": "Meses",
        }

        label = field_labels.get(field_name, field_name)
        output.append(f"## {label}\n\n")

        # Format as table
        output.append("| Item | Quantidade |\n")
        output.append("|------|------------|\n")

        for count_item in counts:
            value = count_item.get("value", "N/A")
            count = count_item.get("count", 0)
            output.append(f"| {value} | {count:,} |\n")

        output.append("\n")

    return "".join(output)


def format_document_full(document: dict[str, Any]) -> str:
    """
    Format a single document in full detail.

    Args:
        document: Document dictionary

    Returns:
        Markdown-formatted string with full document
    """
    output = []

    # Title
    if title := document.get("title"):
        output.append(f"# {title}\n\n")

    # Metadata section
    output.append("## Metadados\n\n")

    metadata = []
    if unique_id := document.get("unique_id"):
        metadata.append(f"**ID:** {unique_id}")

    if agency := document.get("agency"):
        metadata.append(f"**Agência:** {agency}")

    if published_at := document.get("published_at"):
        date_str = format_timestamp(published_at)
        metadata.append(f"**Publicado:** {date_str}")

    if category := document.get("category"):
        metadata.append(f"**Categoria:** {category}")

    if theme := document.get("theme_1_level_1"):
        metadata.append(f"**Tema Principal:** {theme}")

    if url := document.get("url"):
        metadata.append(f"**URL:** {url}")

    if image := document.get("image"):
        metadata.append(f"**Imagem:** {image}")

    output.append(" | ".join(metadata))
    output.append("\n\n")

    # Content
    if content := document.get("content"):
        output.append("## Conteúdo\n\n")
        output.append(content)
        output.append("\n")

    return "".join(output)
