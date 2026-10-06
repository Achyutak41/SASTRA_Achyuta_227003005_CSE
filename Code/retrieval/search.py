import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


INDEX_FILE = Path(
    "Input_Data/processed/EcuExtract.faiss"
)

METADATA_FILE = Path(
    "Input_Data/processed/EcuExtract_metadata.json"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def load_retriever():

    model = SentenceTransformer(MODEL_NAME)

    index = faiss.read_index(
        str(INDEX_FILE)
    )

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = json.load(file)

    return model, index, metadata


def search(query, model, index, metadata, top_k=5):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(query_embedding)

    # Retrieve a larger candidate pool first.
    candidate_k = min(10, index.ntotal)

    scores, indices = index.search(
        query_embedding,
        candidate_k
    )

    query_lower = query.lower()

    results = []

    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id == -1:
            continue

        item = metadata[index_id]

        text_lower = item["text"].lower()

        final_score = float(score)

        # -----------------------------------------------------
        # Intent-aware reranking
        # -----------------------------------------------------

        # PROVIDES intent
        if any(
            word in query_lower
            for word in [
                "provide",
                "provides",
                "provided"
            ]
        ):

            if "provides" in text_lower:
                final_score += 0.15

            if "provides_interface" in text_lower:
                final_score += 0.10

        # REQUIRES intent
        if any(
            word in query_lower
            for word in [
                "require",
                "requires",
                "required"
            ]
        ):

            if "requires" in text_lower:
                final_score += 0.15

            if "requires_interface" in text_lower:
                final_score += 0.10

        # CONNECTOR intent
        if any(
            word in query_lower
            for word in [
                "connect",
                "connected",
                "connection"
            ]
        ):

            if "connector" in text_lower:
                final_score += 0.15

        # RUNNABLE intent
        if "runnable" in query_lower:

            if "runnable" in text_lower:
                final_score += 0.15

        # -----------------------------------------------------
        # Exact phrase/entity matching
        # -----------------------------------------------------

        query_words = (
            query_lower
            .replace("?", "")
            .replace(",", "")
            .split()
        )

        exact_matches = sum(
            1
            for word in query_words
            if len(word) > 3
            and word in text_lower
        )

        final_score += (
            0.01 * exact_matches
        )

        results.append({
            "score": float(score),
            "final_score": final_score,
            "chunk_id": item["chunk_id"],
            "chunk_type": item["chunk_type"],
            "text": item["text"],
            "source": item["source"]
        })

    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return results[:top_k]

def main():

    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_FILE}"
        )

    if not METADATA_FILE.exists():
        raise FileNotFoundError(
            f"Metadata not found: {METADATA_FILE}"
        )

    print("=" * 60)
    print("AUTOSAR SEMANTIC RETRIEVAL")
    print("=" * 60)

    print("\nLoading retrieval model...")

    model, index, metadata = load_retriever()

    print(
        f"Indexed chunks: {index.ntotal}"
    )

    query = input(
        "\nEnter your AUTOSAR question: "
    ).strip()

    if not query:
        print("No query entered.")
        return

    results = search(
        query,
        model,
        index,
        metadata,
        top_k=5
    )

    print("\n" + "=" * 60)
    print("RETRIEVAL RESULTS")
    print("=" * 60)

    for position, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n[{position}] "
            f"Semantic: {result['score']:.4f} "
            f"Final: {result['final_score']:.4f}"
        )

        print(
            f"Chunk: {result['chunk_id']}"
        )

        print(
            f"Type: {result['chunk_type']}"
        )

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Text: {result['text']}"
        )


if __name__ == "__main__":
    main()