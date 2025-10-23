"""Tests for temporal analysis tool and utilities."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from govbrnews_mcp.tools.temporal import analyze_temporal
from govbrnews_mcp.utils.temporal import (
    get_temporal_distribution,
    format_temporal_distribution,
    _get_month_name,
)


class TestTemporalUtils:
    """Tests for temporal utility functions."""

    def test_get_month_name(self):
        """Test month name conversion."""
        assert _get_month_name(1) == "Janeiro"
        assert _get_month_name(6) == "Junho"
        assert _get_month_name(12) == "Dezembro"

    @patch("govbrnews_mcp.utils.temporal.get_typesense_client")
    def test_get_temporal_distribution_yearly(self, mock_get_client):
        """Test yearly temporal distribution."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 10000,
            "facet_counts": [
                {
                    "field_name": "published_year",
                    "counts": [
                        {"value": "2024", "count": 6000},
                        {"value": "2025", "count": 4000}
                    ]
                }
            ]
        }

        result = get_temporal_distribution("educação", "yearly")

        assert result["granularity"] == "yearly"
        assert result["query"] == "educação"
        assert result["total_found"] == 10000
        assert len(result["distribution"]) == 2
        assert result["distribution"][0]["period"] == "2024"
        assert result["distribution"][0]["count"] == 6000

    @patch("govbrnews_mcp.utils.temporal.get_typesense_client")
    def test_get_temporal_distribution_yearly_with_filters(self, mock_get_client):
        """Test yearly distribution with year filters."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 5000,
            "facet_counts": [
                {
                    "field_name": "published_year",
                    "counts": [{"value": "2024", "count": 5000}]
                }
            ]
        }

        result = get_temporal_distribution("saúde", "yearly", year_from=2024, year_to=2024)

        assert result["filters"]["year_from"] == 2024
        assert result["filters"]["year_to"] == 2024

        # Verificar que filtro foi usado
        call_args = mock_client.client.collections.__getitem__.return_value.documents.search.call_args
        assert "filter_by" in call_args[0][0]
        assert "published_year:>=2024" in call_args[0][0]["filter_by"]
        assert "published_year:<=2024" in call_args[0][0]["filter_by"]

    @patch("govbrnews_mcp.utils.temporal.get_typesense_client")
    def test_get_temporal_distribution_monthly(self, mock_get_client):
        """Test monthly temporal distribution."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock inicial para descobrir anos
        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 2000,
            "facet_counts": [
                {
                    "field_name": "published_year",
                    "counts": [{"value": "2025", "count": 2000}]
                },
                {
                    "field_name": "published_month",
                    "counts": [
                        {"value": "1", "count": 1000},
                        {"value": "2", "count": 1000}
                    ]
                }
            ]
        }

        # Mock queries mensais subsequentes
        def search_side_effect(params):
            if "published_month:=1" in params.get("filter_by", ""):
                return {"found": 1000}
            elif "published_month:=2" in params.get("filter_by", ""):
                return {"found": 1000}
            else:
                return {"found": 0}

        mock_client.client.collections.__getitem__.return_value.documents.search.side_effect = search_side_effect

        result = get_temporal_distribution("educação", "monthly", year_from=2025, year_to=2025, max_periods=12)

        assert result["granularity"] == "monthly"
        assert result["query"] == "educação"
        assert "note" in result

    @patch("govbrnews_mcp.utils.temporal.get_typesense_client")
    def test_get_temporal_distribution_weekly(self, mock_get_client):
        """Test weekly temporal distribution."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock para queries semanais
        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 100
        }

        result = get_temporal_distribution("saúde", "weekly", max_periods=4)

        assert result["granularity"] == "weekly"
        assert result["query"] == "saúde"
        assert "distribution" in result
        assert "note" in result
        assert "semanal" in result["note"]
        assert len(result["distribution"]) <= 4

    @patch("govbrnews_mcp.utils.temporal.get_typesense_client")
    def test_get_temporal_distribution_weekly_limits(self, mock_get_client):
        """Test that weekly distribution is limited to 52 weeks."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.client.collections.__getitem__.return_value.documents.search.return_value = {
            "found": 50
        }

        result = get_temporal_distribution("test", "weekly", max_periods=100)

        # Should be limited to 52
        assert len(result["distribution"]) <= 52

    def test_get_temporal_distribution_invalid_granularity(self):
        """Test invalid granularity returns error in dict."""
        result = get_temporal_distribution("test", "invalid")

        assert "error" in result
        assert "Granularidade inválida" in result["error"]

    def test_format_temporal_distribution_success(self):
        """Test formatting temporal distribution."""
        data = {
            "granularity": "monthly",
            "query": "educação",
            "total_found": 5000,
            "distribution": [
                {"period": "2025-01", "label": "Janeiro/2025", "count": 2000},
                {"period": "2025-02", "label": "Fevereiro/2025", "count": 3000}
            ],
            "filters": {"year_from": 2025, "year_to": 2025}
        }

        result = format_temporal_distribution(data)

        assert "# Distribuição Temporal" in result
        assert "educação" in result
        assert "monthly" in result
        assert "5,000" in result
        assert "Janeiro/2025" in result
        assert "2,000" in result
        assert "Fevereiro/2025" in result
        assert "3,000" in result

    def test_format_temporal_distribution_with_error(self):
        """Test formatting when there's an error."""
        data = {
            "error": "Connection failed",
            "granularity": "monthly",
            "query": "test"
        }

        result = format_temporal_distribution(data)

        assert "# Erro na Análise Temporal" in result
        assert "Connection failed" in result

    def test_format_temporal_distribution_empty(self):
        """Test formatting with no distribution data."""
        data = {
            "granularity": "yearly",
            "query": "xyz",
            "total_found": 0,
            "distribution": [],
            "filters": {}
        }

        result = format_temporal_distribution(data)

        assert "Nenhum dado encontrado" in result


class TestAnalyzeTemporalTool:
    """Tests for analyze_temporal tool."""

    @patch("govbrnews_mcp.tools.temporal.get_temporal_distribution")
    def test_analyze_temporal_monthly_success(self, mock_get_dist):
        """Test successful monthly temporal analysis."""
        mock_get_dist.return_value = {
            "granularity": "monthly",
            "query": "educação",
            "total_found": 5000,
            "distribution": [
                {"period": "2025-01", "label": "Janeiro/2025", "count": 2000},
                {"period": "2025-02", "label": "Fevereiro/2025", "count": 3000}
            ],
            "filters": {"year_from": 2025, "year_to": 2025}
        }

        result = analyze_temporal("educação", "monthly", 2025, 2025)

        assert "# Distribuição Temporal" in result
        assert "educação" in result
        assert "Janeiro/2025" in result

    @patch("govbrnews_mcp.tools.temporal.get_temporal_distribution")
    def test_analyze_temporal_yearly(self, mock_get_dist):
        """Test yearly temporal analysis."""
        mock_get_dist.return_value = {
            "granularity": "yearly",
            "query": "saúde",
            "total_found": 10000,
            "distribution": [
                {"period": "2024", "label": "2024", "count": 6000},
                {"period": "2025", "label": "2025", "count": 4000}
            ],
            "filters": {}
        }

        result = analyze_temporal("saúde", "yearly")

        assert "# Distribuição Temporal" in result
        assert "yearly" in result

    @patch("govbrnews_mcp.tools.temporal.get_temporal_distribution")
    def test_analyze_temporal_weekly(self, mock_get_dist):
        """Test weekly temporal analysis."""
        mock_get_dist.return_value = {
            "granularity": "weekly",
            "query": "meio ambiente",
            "total_found": 500,
            "distribution": [
                {"period": "2025-W01", "label": "Semana de 01/01/2025", "count": 250},
                {"period": "2025-W02", "label": "Semana de 08/01/2025", "count": 250}
            ],
            "filters": {},
            "note": "Distribuição semanal limitada a 52 semanas"
        }

        result = analyze_temporal("meio ambiente", "weekly", max_periods=2)

        assert "# Distribuição Temporal" in result
        assert "weekly" in result
        assert "Semana de" in result

    def test_analyze_temporal_invalid_granularity(self):
        """Test with invalid granularity."""
        result = analyze_temporal("test", "invalid")

        assert "# Erro" in result
        assert "Granularidade inválida" in result
        assert "yearly" in result
        assert "monthly" in result
        assert "weekly" in result

    @patch("govbrnews_mcp.tools.temporal.get_temporal_distribution")
    def test_analyze_temporal_limits_yearly(self, mock_get_dist):
        """Test that yearly max_periods is limited to 50."""
        mock_get_dist.return_value = {
            "granularity": "yearly",
            "query": "test",
            "total_found": 100,
            "distribution": [],
            "filters": {}
        }

        analyze_temporal("test", "yearly", max_periods=100)

        # Verify it was called with max 50
        call_args = mock_get_dist.call_args
        assert call_args[1]["max_periods"] == 50

    @patch("govbrnews_mcp.tools.temporal.get_temporal_distribution")
    def test_analyze_temporal_limits_monthly(self, mock_get_dist):
        """Test that monthly max_periods is limited to 60."""
        mock_get_dist.return_value = {
            "granularity": "monthly",
            "query": "test",
            "total_found": 100,
            "distribution": [],
            "filters": {}
        }

        analyze_temporal("test", "monthly", max_periods=100)

        # Verify it was called with max 60
        call_args = mock_get_dist.call_args
        assert call_args[1]["max_periods"] == 60

    @patch("govbrnews_mcp.tools.temporal.get_temporal_distribution")
    def test_analyze_temporal_limits_weekly(self, mock_get_dist):
        """Test that weekly max_periods is limited to 52."""
        mock_get_dist.return_value = {
            "granularity": "weekly",
            "query": "test",
            "total_found": 100,
            "distribution": [],
            "filters": {},
            "note": "Limited"
        }

        analyze_temporal("test", "weekly", max_periods=100)

        # Verify it was called with max 52
        call_args = mock_get_dist.call_args
        assert call_args[1]["max_periods"] == 52

    @patch("govbrnews_mcp.tools.temporal.get_temporal_distribution")
    def test_analyze_temporal_error_handling(self, mock_get_dist):
        """Test error handling in analyze_temporal."""
        mock_get_dist.side_effect = Exception("Database error")

        result = analyze_temporal("test", "monthly")

        assert "# Erro na Análise Temporal" in result
        assert "Database error" in result
