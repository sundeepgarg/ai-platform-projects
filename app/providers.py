from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.models import KnowledgeDocument


@dataclass(frozen=True)
class ProviderResponse:
    provider: str
    model: str
    answer: str


class MockProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, question: str, context_docs: list[KnowledgeDocument]) -> ProviderResponse:
        if not context_docs:
            answer = (
                "I could not find relevant enterprise platform context in the local knowledge base. "
                "Try a more specific question or expand the platform documents."
            )
        else:
            snippets = []
            for doc in context_docs:
                first_sentence = doc.content.split(".")[0].strip()
                snippets.append(f"- {doc.title}: {first_sentence}.")
            answer = (
                f"Answer for: {question}\n\n"
                "Platform summary:\n"
                f"{chr(10).join(snippets)}\n\n"
                "This answer was generated in mock mode to help you learn the request flow safely."
            )

        return ProviderResponse(
            provider="mock",
            model="deterministic-platform-simulator",
            answer=answer,
        )


class BedrockProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, question: str, context_docs: list[KnowledgeDocument]) -> ProviderResponse:
        import boto3

        prompt = self._build_prompt(question=question, context_docs=context_docs)
        client = boto3.client("bedrock-runtime", region_name=self.settings.aws_region)
        response = client.converse(
            modelId=self.settings.bedrock_model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
        )
        output_text = response["output"]["message"]["content"][0]["text"]
        return ProviderResponse(
            provider="bedrock",
            model=self.settings.bedrock_model_id,
            answer=output_text,
        )

    @staticmethod
    def _build_prompt(question: str, context_docs: list[KnowledgeDocument]) -> str:
        context_lines = []
        for doc in context_docs:
            context_lines.append(
                f"Title: {doc.title}\nTags: {', '.join(doc.tags)}\nContent: {doc.content}"
            )

        joined_context = "\n\n".join(context_lines) if context_lines else "No matching context provided."
        return (
            "You are an enterprise AI platform assistant. "
            "Answer using the provided platform context. "
            "If the context is insufficient, say so clearly.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{joined_context}"
        )


def get_provider(settings: Settings) -> MockProvider | BedrockProvider:
    if settings.llm_provider == "bedrock":
        return BedrockProvider(settings)
    return MockProvider(settings)

