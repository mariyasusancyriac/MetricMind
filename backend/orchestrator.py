import os
import json
import requests
from typing import Dict, Any, List

class AgenticSemanticOrchestrator:
    """
    Orchestration interface routing natural language prompts
    to governed Semantic Layer API endpoints rather than raw Text-to-SQL.
    """
    def __init__(self, backend_api_url: str = "http://127.0.0.1:8000"):
        self.backend_api_url = backend_api_url
        self.semantic_context = self._load_semantic_context()

    def _load_semantic_context(self) -> Dict[str, Any]:
        """Loads certified dimensional and metric schemas for LLM context grounding."""
        return {
            "cube": "EnterpriseFinance",
            "available_dimensions": ["quarter", "region", "product_line"],
            "available_measures": ["total_revenue", "total_cogs", "total_operating_expense", "net_margin", "profit_margin_pct"]
        }

    def parse_intent_to_semantic_payload(self, user_query: str) -> Dict[str, Any]:
        """
        Translates executive questions into governed JSON query payloads.
        Prevents arbitrary table joins and SQL hallucinations.
        """
        query_lower = user_query.lower()

        # Regional margin anomaly query mapping
        if "europe" in query_lower and ("margin" in query_lower or "drop" in query_lower):
            return {
                "dimensions": ["quarter", "region"],
                "measures": ["total_revenue", "total_cogs", "net_margin", "profit_margin_pct"],
                "filters": {"region": "Europe"}
            }
        
        # Product line revenue breakdown mapping
        if "product" in query_lower or "line" in query_lower:
            return {
                "dimensions": ["quarter", "product_line"],
                "measures": ["total_revenue", "net_margin", "profit_margin_pct"],
                "filters": {}
            }

        # Default high-level quarter-over-quarter trend
        return {
            "dimensions": ["quarter"],
            "measures": ["total_revenue", "net_margin", "profit_margin_pct"],
            "filters": {}
        }

    def execute_governed_query(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches the certified semantic request to the backend service."""
        endpoint = f"{self.backend_api_url}/query-metrics"
        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "message": f"Backend returned HTTP {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Connection to Semantic API failed: {str(e)}"}