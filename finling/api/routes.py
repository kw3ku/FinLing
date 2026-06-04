"""
FastAPI routes for FinLing.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from finling.pipeline.core import FinLingPipeline, QueryResult
from finling.languages.registry import supported_languages

app = FastAPI(
    title="FinLing API",
    description="Financial intelligence in African languages — starting with Ghana.",
    version="0.1.0",
)

_pipeline = FinLingPipeline()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="The user's question")
    lang_code: str | None = Field(None, description="Optional BCP-47 language code, e.g. 'tw'")


class QueryResponse(BaseModel):
    detected_language: str
    english_query: str
    response_en: str
    response_local: str
    concepts_matched: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", summary="Health check")
def root() -> dict[str, str]:
    return {"status": "ok", "project": "FinLing", "version": "0.1.0"}


@app.get("/languages", summary="List supported languages")
def list_languages() -> list[dict]:
    return [
        {
            "code": lang.code,
            "name": lang.name,
            "native_name": lang.native_name,
            "region": lang.region,
        }
        for lang in supported_languages()
    ]


@app.post("/query", response_model=QueryResponse, summary="Ask a financial question")
def query(request: QueryRequest) -> QueryResponse:
    try:
        result: QueryResult = _pipeline.query(request.text, request.lang_code)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return QueryResponse(
        detected_language=result.detected_language,
        english_query=result.english_query,
        response_en=result.response_en,
        response_local=result.response_local,
        concepts_matched=len(result.concepts),
    )
