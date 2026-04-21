import re

from app.models import KnowledgeDocument, RetrievedSource


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9-]+")


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


class Retriever:
    def __init__(self, documents: list[KnowledgeDocument]) -> None:
        self.documents = documents

    def search(self, query: str, top_k: int = 3) -> list[RetrievedSource]:
        query_tokens = tokenize(query)
        scored: list[RetrievedSource] = []

        for document in self.documents:
            searchable_text = " ".join([document.title, document.content, " ".join(document.tags)])
            document_tokens = tokenize(searchable_text)
            overlap = query_tokens & document_tokens
            if not overlap:
                continue

            score = round(len(overlap) / max(len(query_tokens), 1), 3)
            scored.append(
                RetrievedSource(
                    id=document.id,
                    title=document.title,
                    score=score,
                    tags=document.tags,
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def get_documents_by_ids(self, ids: list[str]) -> list[KnowledgeDocument]:
        by_id = {document.id: document for document in self.documents}
        return [by_id[item_id] for item_id in ids if item_id in by_id]

