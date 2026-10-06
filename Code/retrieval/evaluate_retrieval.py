import json
from pathlib import Path

from search import load_retriever, search


QUERY_FILE = Path(
    "Evaluation_Results/retrieval_queries.json"
)

OUTPUT_FILE = Path(
    "Evaluation_Results/retrieval_results.json"
)


def main():

    with open(
        QUERY_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        queries = json.load(file)

    model, index, metadata = load_retriever()

    results = []

    for item in queries:

        query = item["query"]
        expected_keywords = [
            keyword.lower()
            for keyword in item["expected_keywords"]
        ]

        retrieved = search(
            query,
            model,
            index,
            metadata,
            top_k=5
        )

        top_result = retrieved[0]

        top_text = top_result["text"].lower()

        matched = [
            keyword
            for keyword in expected_keywords
            if keyword in top_text
        ]

        passed = (
            len(matched) == len(expected_keywords)
        )

        results.append({
            "query": query,
            "top_chunk": top_result["chunk_id"],
            "top_score": top_result["score"],
            "top_text": top_result["text"],
            "expected_keywords": expected_keywords,
            "matched_keywords": matched,
            "passed": passed
        })

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    passed_count = sum(
        result["passed"]
        for result in results
    )

    print("=" * 60)
    print("RETRIEVAL EVALUATION")
    print("=" * 60)

    print(
        f"\nQueries tested: {len(results)}"
    )

    print(
        f"Passed: {passed_count}"
    )

    print(
        f"Failed: {len(results) - passed_count}"
    )

    print(
        f"\nTop-1 keyword success: "
        f"{passed_count / len(results) * 100:.2f}%"
    )

    for number, result in enumerate(
        results,
        start=1
    ):

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"\n[{number}] {status}"
        )

        print(
            f"Query: {result['query']}"
        )

        print(
            f"Top chunk: {result['top_chunk']}"
        )

        print(
            f"Score: {result['top_score']:.4f}"
        )

        print(
            f"Text: {result['top_text']}"
        )

    print(
        f"\nResults saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()