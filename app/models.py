from typing import List, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=2000)
    top_k: int = Field(3, ge=1, le=5)


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    top_k: int = Field(3, ge=1, le=5)


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str]


class RetrievedSource(BaseModel):
    id: str
    title: str
    score: float
    tags: List[str]


class TraceStep(BaseModel):
    name: str
    detail: str


class GuardrailResult(BaseModel):
    status: Literal["allowed", "blocked"]
    reasons: List[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    request_id: str
    provider: str
    model: str
    prompt_version: str
    guardrails: GuardrailResult
    answer: str
    sources: List[RetrievedSource]
    trace: List[TraceStep]


class RetrieveResponse(BaseModel):
    request_id: str
    results: List[RetrievedSource]
    trace: List[TraceStep]


class EvalCaseResult(BaseModel):
    question: str
    expected_keyword: str
    passed: bool
    answer_preview: str


class EvalRunResponse(BaseModel):
    request_id: str
    provider: str
    model: str
    total: int
    passed: int
    failed: int
    results: List[EvalCaseResult]


class HealthResponse(BaseModel):
    status: str
    environment: str
    provider: str
    prompt_version: str

