from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Enterprise Semantic Data API",
    version="1.0.0"
)
class SemanticDimension(BaseModel):
    name: str
    field: str
    description: Optional[str] = None


class SemanticMeasure(BaseModel):
    name: str
    field: str
    aggregation: str
    description: Optional[str] = None
@app.post("/semantic/dimensions")
def create_dimension(dimension: SemanticDimension):
    return {
        "message": "Semantic dimension created",
        "dimension": dimension
    }


@app.post("/semantic/measures")
def create_measure(measure: SemanticMeasure):
    return {
        "message": "Semantic measure created",
        "measure": measure
    }

@app.get("/")
def root():
    return {
        "message": "Enterprise Semantic Data API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }