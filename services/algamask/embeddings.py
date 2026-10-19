from typing import Protocol


class EmbeddingProvider(Protocol):
    """Integration boundary for a future configured embedding model."""

    def embed(self, texts: list[str]) -> list[list[float]]: ...
