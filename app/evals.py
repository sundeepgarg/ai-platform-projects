import json
from pathlib import Path


def load_eval_cases(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

