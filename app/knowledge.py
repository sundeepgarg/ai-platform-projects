import json
from pathlib import Path

from app.models import KnowledgeDocument


def load_knowledge_base(path: str) -> list[KnowledgeDocument]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [KnowledgeDocument(**item) for item in payload]

