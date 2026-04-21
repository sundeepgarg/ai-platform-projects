from __future__ import annotations

import uuid

from app.config import Settings
from app.guardrails import GuardrailEngine
from app.models import (
    ChatResponse,
    EvalCaseResult,
    EvalRunResponse,
    RetrievedSource,
    RetrieveResponse,
    TraceStep,
)
from app.providers import get_provider
from app.retrieval import Retriever
from app.knowledge import load_knowledge_base
from app.evals import load_eval_cases


class AIPlatformService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.documents = load_knowledge_base(settings.knowledge_base_path)
        self.retriever = Retriever(self.documents)
        self.guardrails = GuardrailEngine()
        self.provider = get_provider(settings)

    def retrieve(self, query: str, top_k: int) -> RetrieveResponse:
        request_id = str(uuid.uuid4())
        results = self.retriever.search(query=query, top_k=top_k)
        trace = [
            TraceStep(name="request_received", detail="Retrieval request accepted."),
            TraceStep(name="retrieval_completed", detail=f"Returned {len(results)} result(s)."),
        ]
        return RetrieveResponse(request_id=request_id, results=results, trace=trace)

    def chat(self, question: str, top_k: int) -> ChatResponse:
        request_id = str(uuid.uuid4())
        trace = [TraceStep(name="request_received", detail="Chat request accepted.")]

        guardrail_result = self.guardrails.evaluate(question)
        trace.append(
            TraceStep(
                name="guardrails_checked",
                detail=f"Guardrail status: {guardrail_result.status}.",
            )
        )

        if guardrail_result.status == "blocked":
            trace.append(
                TraceStep(name="provider_skipped", detail="Model call skipped because request was blocked.")
            )
            return ChatResponse(
                request_id=request_id,
                provider="none",
                model="none",
                prompt_version=self.settings.prompt_version,
                guardrails=guardrail_result,
                answer="Request blocked by platform guardrails.",
                sources=[],
                trace=trace,
            )

        source_hits = self.retriever.search(query=question, top_k=top_k)
        trace.append(
            TraceStep(name="retrieval_completed", detail=f"Retrieved {len(source_hits)} supporting source(s).")
        )

        context_docs = self.retriever.get_documents_by_ids([item.id for item in source_hits])
        trace.append(
            TraceStep(
                name="context_assembled",
                detail=f"Prepared {len(context_docs)} context document(s) for provider execution.",
            )
        )

        generated = self.provider.generate(question=question, context_docs=context_docs)
        trace.append(
            TraceStep(
                name="provider_completed",
                detail=f"Provider '{generated.provider}' returned an answer.",
            )
        )

        return ChatResponse(
            request_id=request_id,
            provider=generated.provider,
            model=generated.model,
            prompt_version=self.settings.prompt_version,
            guardrails=guardrail_result,
            answer=generated.answer,
            sources=source_hits,
            trace=trace,
        )

    def run_evals(self) -> EvalRunResponse:
        request_id = str(uuid.uuid4())
        cases = load_eval_cases(self.settings.eval_dataset_path)
        results: list[EvalCaseResult] = []

        for case in cases:
            response = self.chat(question=case["question"], top_k=case.get("top_k", 3))
            passed = case["expected_keyword"].lower() in response.answer.lower()
            results.append(
                EvalCaseResult(
                    question=case["question"],
                    expected_keyword=case["expected_keyword"],
                    passed=passed,
                    answer_preview=response.answer[:160],
                )
            )

        passed_count = sum(1 for item in results if item.passed)
        return EvalRunResponse(
            request_id=request_id,
            provider=self.settings.llm_provider,
            model=self.settings.bedrock_model_id if self.settings.llm_provider == "bedrock" else "deterministic-platform-simulator",
            total=len(results),
            passed=passed_count,
            failed=len(results) - passed_count,
            results=results,
        )

