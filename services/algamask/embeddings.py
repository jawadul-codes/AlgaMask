import os
from typing import Protocol

# Small local corpus: avoid competing native thread pools on macOS.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
DIMENSIONS = 384


class EmbeddingProvider(Protocol):
    """Local model boundary; implementations must identify their exact configuration."""

    identity: dict

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class LocalSentenceEmbeddings:
    identity = {"model": MODEL_ID, "revision": MODEL_REVISION, "dimensions": DIMENSIONS,
                "normalized": True, "device": "cpu"}

    def __init__(self, *, allow_download: bool = False):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(MODEL_ID, revision=MODEL_REVISION, device="cpu",
                                         trust_remote_code=False, local_files_only=not allow_download)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.model.encode(texts, batch_size=32, normalize_embeddings=True,
                                 show_progress_bar=False, convert_to_numpy=True).tolist()


class LocalReranker:
    identity = {"model": "cross-encoder/ms-marco-MiniLM-L6-v2",
                "revision": "233902d25c440f23af6f7d6e94d2946bac0bee0a", "precision": "float64"}

    def __init__(self, *, allow_download: bool = False):
        from sentence_transformers import CrossEncoder
        import torch

        self.model = CrossEncoder(self.identity["model"], revision=self.identity["revision"],
                                  device="cpu", trust_remote_code=False, local_files_only=not allow_download,
                                  model_kwargs={"torch_dtype": torch.float32, "attn_implementation": "eager"})
        # Float32 inference yielded NaNs on the target macOS native runtime.
        self.model.model.double()

    def score(self, query: str, passages: list[str]) -> list[float]:
        return self.model.predict([(query, passage) for passage in passages], batch_size=32,
                                  show_progress_bar=False).tolist()
