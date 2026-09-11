from typing import Dict, Any, List

class QueryCostGovernor:
    """
    Cost Governance & Complexity Circuit-Breaker Middleware.
    Evaluates query breadth and compute risk before hitting the analytical data layer.
    """
    def __init__(
        self,
        max_allowed_dimensions: int = 3,
        max_allowed_measures: int = 4,
        max_scan_rows_limit: int = 50000,
        token_cost_threshold: int = 150
    ):
        self.max_allowed_dimensions = max_allowed_dimensions
        self.max_allowed_measures = max_allowed_measures
        self.max_scan_rows_limit = max_scan_rows_limit
        self.token_cost_threshold = token_cost_threshold

    def estimate_complexity(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates an empirical complexity score based on dimensional cross-products
        and requested aggregations.
        """
        dims: List[str] = payload.get("dimensions", [])
        measures: List[str] = payload.get("measures", [])
        filters: Dict[str, Any] = payload.get("filters", {})

        # Calculate dimensional depth penalty
        dim_count = len(dims)
        measure_count = len(measures)

        # Base token overhead + dynamic query weight
        estimated_token_weight = (dim_count * 25) + (measure_count * 15) + (len(filters) * 10)

        # Unbounded full-table scan evaluation
        estimated_row_scan = 1500 if filters else 1500 * (dim_count if dim_count > 0 else 1)

        return {
            "dimension_count": dim_count,
            "measure_count": measure_count,
            "estimated_token_cost": estimated_token_weight,
            "estimated_rows_scanned": estimated_row_scan,
            "has_filters": bool(filters)
        }

    def evaluate_query(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Circuit-breaker audit: rejects expensive or unbounded queries.
        """
        metrics = self.estimate_complexity(payload)

        # Dimension explosion check
        if metrics["dimension_count"] > self.max_allowed_dimensions:
            return {
                "allowed": False,
                "reason": (
                    f"Governance Rejection: Requested {metrics['dimension_count']} dimensions. "
                    f"Maximum allowed dimension depth is {self.max_allowed_dimensions}."
                ),
                "metrics": metrics
            }

        # Measure overload check
        if metrics["measure_count"] > self.max_allowed_measures:
            return {
                "allowed": False,
                "reason": (
                    f"Governance Rejection: Requested {metrics['measure_count']} measures. "
                    f"Maximum allowed measure limit is {self.max_allowed_measures}."
                ),
                "metrics": metrics
            }

        # Scan boundary check
        if metrics["estimated_rows_scanned"] > self.max_scan_rows_limit:
            return {
                "allowed": False,
                "reason": "Governance Rejection: Query exceeds safe row scanning limits.",
                "metrics": metrics
            }

        # Determine execution risk classification
        risk_tier = "LOW" if metrics["estimated_token_cost"] < 80 else "MEDIUM"
        if metrics["estimated_token_cost"] >= self.token_cost_threshold:
            risk_tier = "HIGH"

        return {
            "allowed": True,
            "risk_tier": risk_tier,
            "metrics": metrics
        }