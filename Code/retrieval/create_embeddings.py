import json
from pathlib import Path

from sentence_transformers import SentenceTransformer


INPUT_FILE = Path(
    "Input_Data/processed/EcuExtract_chunks.json"
)

OUTPUT_FILE = Path(
    "Input_Data/processed/EcuExtract_embeddings.json"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Chunk file not found: {INPUT_FILE}"
        )

    print("=" * 60)
    print("AUTOSAR EMBEDDING GENERATION")
    print("=" * 60)

    print(f"\nLoading model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(f"Chunks to embed: {len(texts)}")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    output = []

    for chunk, embedding in zip(
        chunks,
        embeddings
    ):

        output.append({
            "chunk_id": chunk["chunk_id"],
            "chunk_type": chunk["chunk_type"],
            "text": chunk["text"],
            "source": chunk["source"],
            "embedding": embedding.tolist()
        })

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2
        )

    print(
        f"\nEmbedding dimension: "
        f"{embeddings.shape[1]}"
    )

    print(
        f"Embeddings generated: "
        f"{embeddings.shape[0]}"
    )

    print(
        f"\nOutput: {OUTPUT_FILE}"
    )

    print("\nEmbedding generation completed successfully.")


if __name__ == "__main__":
    main()