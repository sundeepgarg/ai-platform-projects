from fastapi import FastAPI, HTTPException

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, HealthResponse, RetrieveRequest, RetrieveResponse, EvalRunResponse
from app.platform import AIPlatformService


settings = get_settings()
service = AIPlatformService(settings)

app = FastAPI(
    title="Enterprise AI Platform Starter",
    version="1.0.0",
    description="Learning-first AI platform project with guardrails, retrieval, provider abstraction, and evaluations.",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        provider=settings.llm_provider,
        prompt_version=settings.prompt_version,
    )


@app.get("/knowledge-base")
def knowledge_base() -> dict[str, list[str]]:
    return {"documents": [document.title for document in service.documents]}


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    return service.retrieve(query=request.query, top_k=request.top_k)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return service.chat(question=request.question, top_k=request.top_k)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Provider failure: {exc}") from exc


@app.post("/evals/run", response_model=EvalRunResponse)
def run_evals() -> EvalRunResponse:
    try:
        return service.run_evals()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Evaluation failure: {exc}") from exc

