"""Explicit retrieval configuration and one offline model/index instance per process."""
import logging
import os
from pathlib import Path
from threading import Lock
from typing import Literal

from pydantic import BaseModel, ConfigDict

ROOT = Path(__file__).resolve().parents[2]
logger = logging.getLogger(__name__)


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)
    mode: Literal["mock", "development", "production"] = "mock"
    dataset_path: Path = ROOT / "data/candidates/0.1.0-rc.1"
    index_path: Path = ROOT / "indexes/reviewed_evidence/0.1.0-dev.2"
    generation_provider: Literal["extractive", "ollama"] = "extractive"
    generation_model: str = "llama3.2:latest"
    ollama_url: str = "http://127.0.0.1:11434"

    @classmethod
    def from_env(cls):
        values = {field: os.environ[key] for field, key in (
            ("mode", "ALGAMASK_MODE"), ("dataset_path", "ALGAMASK_DATASET_PATH"),
            ("index_path", "ALGAMASK_INDEX_PATH"), ("generation_provider", "ALGAMASK_GENERATION_PROVIDER"),
            ("generation_model", "ALGAMASK_GENERATION_MODEL"), ("ollama_url", "ALGAMASK_OLLAMA_URL")) if key in os.environ}
        return cls(**values)


class RetrievalUnavailable(RuntimeError):
    pass


class RetrievalRuntime:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._search = None
        self._lock = Lock()
        self.status = "disabled" if settings.mode == "mock" else "not_loaded"

    def generation_provider(self):
        from .generation import ExtractiveProvider, OllamaProvider
        if self.settings.generation_provider == "extractive":
            return ExtractiveProvider()
        return OllamaProvider(self.settings.generation_model, self.settings.ollama_url)

    def get_search(self):
        if self.settings.mode == "mock":
            raise RetrievalUnavailable("Real retrieval is disabled in mock mode")
        with self._lock:
            if self._search is None:
                try:
                    from .embeddings import LocalSentenceEmbeddings
                    from .rag import EvidenceSearch
                    self._search = EvidenceSearch(self.settings.dataset_path, self.settings.index_path,
                                                  LocalSentenceEmbeddings(),
                                                  development=self.settings.mode == "development")
                except Exception as exc:
                    self.status = "unavailable"
                    logger.exception("Retrieval initialization failed")
                    raise RetrievalUnavailable("Local retrieval is unavailable; check dataset, index and cached model configuration") from exc
                self.status = "ready"
            return self._search
