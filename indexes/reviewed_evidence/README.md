# Local evidence indexes

Active development index: `0.1.0-dev.2` (22 evidence chunks, pinned local MiniLM,
normalized FAISS cosine search). `0.1.0-dev.1` is retained as the original experiment.

Both are candidate-only and require explicit development mode. Dataset and model
versions plus content hashes are checked when loading. Never overwrite an index
version; rebuild with a new name after dataset/model/text-preparation changes.

See [local retrieval documentation](../../docs/LOCAL_RETRIEVAL.md) for installation,
offline search, evaluation and the production-release boundary.
