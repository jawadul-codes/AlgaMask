from .fixtures import EVIDENCE


def retrieve_mock() -> list[dict]:
    return [dict(chunk) for chunk in EVIDENCE]


def approved_chunks(rows: list[dict]) -> list[dict]:
    """Future real retrieval must enter through this provenance gate."""
    return [row for row in rows if row.get("review_status") == "approved" and row.get("source_id")]
