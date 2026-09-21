from typing import Dict, Any, List

class QueryCostGovernor:
    def __init__(self, max_allowed_dimensions: int = 3, max_allowed_measures: int = 4):
        self.max_allowed_dimensions = max_allowed_dimensions
        self.max_allowed_measures = max_allowed_measures

    def evaluate_query(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dims: List[str] = payload.get("dimensions", [])
        measures: List[str] = payload.get("measures", [])
        filters: Dict[str, Any] = payload.get("filters", {})

        if len(dims) > self.max_allowed_dimensions:
            return {
                "allowed": False,
                "reason": f"Governor Circuit-Breaker: Requested {len(dims)} dimensions. Max limit is {self.max_allowed_dimensions}."
            }
        if len(measures) > self.max_allowed_measures:
            return {
                "allowed": False,
                "reason": f"Governor Circuit-Breaker: Requested {len(measures)} measures. Max limit is {self.max_allowed_measures}."
            }

        estimated_tokens = (len(dims) * 25) + (len(measures) * 15) + (len(filters) * 10)
        return {
            "allowed": True,
            "estimated_token_cost": estimated_tokens,
            "risk_tier": "LOW" if estimated_tokens < 100 else "MEDIUM"
        }