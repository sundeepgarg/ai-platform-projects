from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    aws_region: str = os.getenv("AWS_REGION", "ap-south-1").strip()
    bedrock_model_id: str = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0").strip()
    knowledge_base_path: str = os.getenv("KNOWLEDGE_BASE_PATH", "data/knowledge_base.json").strip()
    eval_dataset_path: str = os.getenv("EVAL_DATASET_PATH", "data/evals.json").strip()
    prompt_version: str = os.getenv("PROMPT_VERSION", "v1").strip()


def get_settings() -> Settings:
    return Settings()

