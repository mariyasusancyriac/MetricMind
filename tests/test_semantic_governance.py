import pytest
from backend.app import query_metrics, SemanticQuery

def test_governance_audit_metric_determinism():
    """
    Governance Audit: Asserts that querying the semantic layer for a specific
    dimension and measure returns deterministic, identical values every single time
    without LLM SQL hallucinations.
    """
    query = SemanticQuery(
        dimensions=["quarter", "region"],
        measures=["net_margin", "profit_margin_pct"],
        filters={"region": "West"}
    )
    
    # Run the query twice to test numerical determinism
    res1 = query_metrics(query)
    res2 = query_metrics(query)
    
    assert res1["status"] == "success"
    assert res2["status"] == "success"
    assert len(res1["governed_data"]) > 0
    assert res1["governed_data"] == res2["governed_data"], "Governance failure: Hallucinated or non-deterministic metrics detected!"

def test_governance_calculated_measures_exist():
    """Asserts that calculated measures compute successfully."""
    query = SemanticQuery(
        dimensions=["quarter"],
        measures=["total_revenue", "total_cogs", "net_margin", "profit_margin_pct"]
    )
    res = query_metrics(query)
    assert res["status"] == "success"
    first_record = res["governed_data"][0]
    
    for measure in ["total_revenue", "total_cogs", "net_margin", "profit_margin_pct"]:
        assert measure in first_record, f"Missing governed measure: {measure}"
        assert isinstance(first_record[measure], (int, float)), f"Measure {measure} must be numeric"

def test_governance_compiled_sql_transparency():
    """Confirms query transparency by asserting SQL generation exists in the response."""
    query = SemanticQuery(
        dimensions=["product_line"],
        measures=["total_revenue"]
    )
    res = query_metrics(query)
    assert "compiled_sql" in res
    assert "EnterpriseFinance" in res["compiled_sql"]
    assert "GROUP BY" in res["compiled_sql"]