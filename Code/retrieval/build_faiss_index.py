import json
from pathlib import Path

import faiss
import numpy as np


INPUT_FILE = Path(
    "Input_Data/processed/EcuExtract_embeddings.json"
)

INDEX_FILE = Path(
    "Input_Data/processed/EcuExtract.faiss"
)

METADATA_FILE = Path(
    "Input_Data/processed/EcuExtract_metadata.json"
)


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Embedding file not found: {INPUT_FILE}"
        )

    print("=" * 60)
    print("FAISS INDEX CREATION")
    print("=" * 60)

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not data:
        raise ValueError("No embeddings found.")

    embeddings = np.array(
        [
            item["embedding"]
            for item in data
        ],
        dtype="float32"
    )

    print(
        f"\nEmbeddings loaded: "
        f"{len(embeddings)}"
    )

    print(
        f"Embedding dimension: "
        f"{embeddings.shape[1]}"
    )

    # Normalize vectors so inner product behaves
    # like cosine similarity.
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    INDEX_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    faiss.write_index(
        index,
        str(INDEX_FILE)
    )

    # Store metadata separately.
    metadata = []

    for item in data:

        metadata.append({
            "chunk_id": item["chunk_id"],
            "chunk_type": item["chunk_type"],
            "text": item["text"],
            "source": item["source"]
        })

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\nFAISS vectors stored: "
        f"{index.ntotal}"
    )

    print(
        f"FAISS index: {INDEX_FILE}"
    )

    print(
        f"Metadata: {METADATA_FILE}"
    )

    print("\nFAISS index creation completed successfully.")


if __name__ == "__main__":
    main()