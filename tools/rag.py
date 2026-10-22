"""Build, query and evaluate the local evidence index (install the rag extra)."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services"))
from algamask.dataset import load_dataset
from algamask.embeddings import LocalSentenceEmbeddings, LocalReranker
from algamask.publication import canonical
from algamask.rag import EvidenceSearch, SearchRequest, build_index


def evaluate(search: EvidenceSearch, dataset: Path) -> dict:
    results = []
    for row in load_dataset(dataset / "reviewed").records("retrieval_evaluations"):
        if not search.manifest["development_only"] and row.review_status != "approved":
            continue
        filters = json.loads(row.filters) if row.filters else {}
        result = search.search(SearchRequest(**{**filters, "query": row.question, "chunk_tag": row.chunk_tag, "top_k": 20}))
        expected_chunks = set(filter(None, (row.expected_chunk_ids or "").split(";")))
        expected_sources = set(filter(None, (row.expected_source_ids or "").split(";")))
        ranks = [i for i, hit in enumerate(result.hits, 1)
                 if (not expected_chunks or hit.chunk_id in expected_chunks)
                 and (not expected_sources or hit.source_id in expected_sources)]
        rank = min(ranks) if ranks else None
        results.append({"eval_id": row.eval_id, "query": row.question, "review_status": row.review_status,
                        "expected_chunk_ids": sorted(expected_chunks), "first_relevant_rank": rank,
                        "required_rank": row.min_rank, "passed": rank is not None and rank <= row.min_rank,
                        "returned_chunk_ids": [h.chunk_id for h in result.hits]})
    return {"index_version": search.manifest["index_version"], "dataset_hash": search.manifest["dataset_hash"],
            "reranker": search.reranker.identity if search.reranker else None,
            "development_only": search.manifest["development_only"], "question_count": len(results),
            "passed": sum(r["passed"] for r in results),
            "mean_reciprocal_rank": sum(1 / r["first_relevant_rank"] if r["first_relevant_rank"] else 0 for r in results) / len(results) if results else None,
            "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "search", "evaluate"])
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--index", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "indexes/reviewed_evidence")
    parser.add_argument("--version", default="0.1.0-dev.2")
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--download-model", action="store_true", help="Explicitly allow initial model download")
    parser.add_argument("--query")
    parser.add_argument("--tag", choices=["diagnosis", "intervention"])
    parser.add_argument("--species", choices=["spirulina", "chlorella"])
    parser.add_argument("--matrix")
    parser.add_argument("--source-id", action="append", default=[])
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--rerank", action="store_true", help="Experimental optional cross-encoder ranking")
    args = parser.parse_args()
    try:
        provider = LocalSentenceEmbeddings(allow_download=args.download_model)
        if args.command == "build":
            path = build_index(args.dataset, args.output, args.version, provider, development=args.development)
            print(path)
            return 0
        if not args.index:
            parser.error("--index is required for search/evaluate")
        reranker = LocalReranker(allow_download=args.download_model) if args.rerank else None
        search = EvidenceSearch(args.dataset, args.index, provider, development=args.development, reranker=reranker)
        if args.command == "search":
            if not args.query:
                parser.error("--query is required for search")
            result = search.search(SearchRequest(query=args.query, chunk_tag=args.tag, species=args.species,
                                                matrix=args.matrix, source_ids=args.source_id, top_k=args.top_k)).model_dump()
        else:
            result = evaluate(search, args.dataset)
        content = canonical(result)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            with args.report.open("xb") as handle:
                handle.write(content)
        print(content.decode())
        if args.command == "evaluate" and (not result["question_count"] or result["passed"] != result["question_count"]):
            return 1
        return 0
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
