from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from typing import List, Optional, Dict, Any
import os

app = FastAPI(title="MetricMind Semantic Query API", version="1.0.0")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "enterprise_data.csv")

class SemanticQuery(BaseModel):
    dimensions: List[str]
    measures: List[str]
    filters: Optional[Dict[str, Any]] = None

@app.get("/")
def root():
    return {"engine": "MetricMind Governed Semantic Router", "status": "ONLINE"}

@app.post("/query-metrics")
def query_metrics(query: SemanticQuery):
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=404, detail="Enterprise dataset not found.")
    
    df = pd.read_csv(DATA_PATH)
    if query.filters:
        for col, val in query.filters.items():
            if col in df.columns:
                df = df[df[col] == val]

    grouped = df.groupby(query.dimensions) if query.dimensions else df
    results = {}
    if "total_revenue" in query.measures:
        results["total_revenue"] = grouped["gross_revenue"].sum()
    if "total_cogs" in query.measures:
        results["total_cogs"] = grouped["cogs"].sum()
    if "total_operating_expense" in query.measures:
        results["total_operating_expense"] = grouped["operating_expense"].sum()
    if "net_margin" in query.measures:
        results["net_margin"] = grouped["net_margin"].sum()
    if "profit_margin_pct" in query.measures:
        rev = grouped["gross_revenue"].sum()
        margin = grouped["net_margin"].sum()
        results["profit_margin_pct"] = (margin / rev * 100).round(2)

    res_df = pd.DataFrame(results).reset_index()
    return {
        "status": "success",
        "governed_data": res_df.to_dict(orient="records"),
        "compiled_sql": f"SELECT {', '.join(query.dimensions + query.measures)} FROM EnterpriseFinance GROUP BY {', '.join(query.dimensions)}"
    }