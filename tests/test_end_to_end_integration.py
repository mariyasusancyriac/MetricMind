import pytest
import os
import pandas as pd
from backend.cost_governor import QueryCostGovernor
from backend.orchestrator import AgenticSemanticOrchestrator
from backend.app import query_metrics, SemanticQuery

def test_data_pipeline_integrity():
    """Validates that enterprise_data.csv exists, is populated, and has valid columns."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "enterprise_data.csv")
    assert os.path.exists(data_path), "enterprise_data.csv does not exist"
    df = pd.read_csv(data_path)
    assert len(df) > 0, "Dataset contains zero rows"
    expected_cols = ["transaction_id", "quarter", "region", "product_line", "gross_revenue", "cogs", "operating_expense", "net_margin"]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column: {col}"

def test_cost_governor_enforcement():
    """Validates that runaway exploratory queries are stopped by circuit breaker."""
    governor = QueryCostGovernor(max_allowed_dimensions=3, max_allowed_measures=4)
    invalid_payload = {
        "dimensions": ["quarter", "region", "product_line", "transaction_id"],
        "measures": ["total_revenue", "total_cogs", "total_operating_expense", "net_margin", "profit_margin_pct"],
        "filters": {}
    }
    verdict = governor.evaluate_query(invalid_payload)
    assert verdict["allowed"] is False
    assert "limit" in verdict["reason"].lower()

def test_agentic_orchestrator_translation():
    """Validates natural language intent routing to structured semantic JSON."""
    orchestrator = AgenticSemanticOrchestrator()
    payload = orchestrator.translate_to_semantic_payload("Why did our European margins drop last quarter?")
    assert payload["dimensions"] == ["quarter", "region"]
    assert "net_margin" in payload["measures"]
    assert payload["filters"] == {"region": "Europe"}

def test_semantic_query_execution():
    """Validates that certified queries return deterministic aggregated numbers."""
    query = SemanticQuery(
        dimensions=["quarter"],
        measures=["total_revenue", "net_margin", "profit_margin_pct"]
    )
    response = query_metrics(query)
    assert response["status"] == "success"
    assert len(response["governed_data"]) > 0
    first_row = response["governed_data"][0]
    assert "total_revenue" in first_row
    assert "profit_margin_pct" in first_row