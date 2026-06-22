# ─────────────────────────────────────────────
#  config.py — Centralized Settings
# ─────────────────────────────────────────────
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # App
    app_name: str = "AI Doubt Solver Pro"
    app_env: str = "development"
    debug: bool = True

    # LLM Config Fields
    llm_provider_config: str = Field(default="openai", validation_alias="LLM_PROVIDER")
    openai_api_key_config: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_model_config: str = Field(default="gpt-4o", validation_alias="OPENAI_MODEL")
    ollama_base_url_config: str = Field(default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL")
    ollama_model_config: str = Field(default="llama3", validation_alias="OLLAMA_MODEL")
    gemini_api_key_config: str = Field(default="", validation_alias="GEMINI_API_KEY")
    gemini_model_config: str = Field(default="gemini-3.5-flash", validation_alias="GEMINI_MODEL")

    @property
    def llm_provider(self) -> str:
        return os.environ.get("LLM_PROVIDER") or self.llm_provider_config

    @property
    def openai_api_key(self) -> str:
        return os.environ.get("OPENAI_API_KEY") or self.openai_api_key_config

    @property
    def openai_model(self) -> str:
        return os.environ.get("OPENAI_MODEL") or self.openai_model_config

    @property
    def ollama_base_url(self) -> str:
        return os.environ.get("OLLAMA_BASE_URL") or self.ollama_base_url_config

    @property
    def ollama_model(self) -> str:
        return os.environ.get("OLLAMA_MODEL") or self.ollama_model_config

    @property
    def gemini_api_key(self) -> str:
        return os.environ.get("GEMINI_API_KEY") or self.gemini_api_key_config

    @property
    def gemini_model(self) -> str:
        return os.environ.get("GEMINI_MODEL") or self.gemini_model_config

    # Database
    database_url: str = f"sqlite:///{BASE_DIR}/ai_doubt_solver.db"

    # Auth
    jwt_secret_key: str = "change-me-to-a-random-secret-key-32chars"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7 days

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # Uploads
    upload_dir: str = str(BASE_DIR / "uploads")
    max_upload_mb: int = 20

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Language
    default_language: str = "en"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# Ensure required directories exist
for d in [settings.upload_dir, BASE_DIR / "vector_db", BASE_DIR / "uploads"]:
    os.makedirs(d, exist_ok=True)
