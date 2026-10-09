import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class ArchitectureIndexingError(Exception):
    """Raised when architecture knowledge cannot be indexed."""
    pass


class AUTOSARArchitectureIndexer:

    def __init__(
        self,
        processed_dir: str,
        index_dir: str = "Vector_Store"
    ):
        self.processed_dir = Path(processed_dir)
        self.index_dir = Path(index_dir)

        self.index_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def build_index(self, document_id: str):

        input_path = (
            self.processed_dir /
            f"{document_id}_architecture_clean.json"
        )

        if not input_path.exists():
            raise ArchitectureIndexingError(
                f"Clean architecture file not found: {input_path}"
            )

        with open(
            input_path,
            "r",
            encoding="utf-8"
        ) as file:
            architecture = json.load(file)

        records = architecture.get(
            "knowledge_records",
            []
        )

        if not records:
            raise ArchitectureIndexingError(
                "No architecture knowledge records found."
            )

        texts = [
            record["text"]
            for record in records
            if record.get("text")
        ]

        if not texts:
            raise ArchitectureIndexingError(
                "No valid knowledge text available for embedding."
            )

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(
            dimension
        )

        index.add(embeddings)

        index_path = (
            self.index_dir /
            f"{document_id}_architecture.faiss"
        )

        metadata_path = (
            self.index_dir /
            f"{document_id}_architecture_metadata.json"
        )

        faiss.write_index(
            index,
            str(index_path)
        )

        metadata = {
            "document_id": document_id,
            "embedding_model": "all-MiniLM-L6-v2",
            "similarity": "cosine_via_normalized_inner_product",
            "dimension": dimension,
            "record_count": len(texts),
            "records": records
        }

        with open(
            metadata_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                metadata,
                file,
                indent=2,
                ensure_ascii=False
            )

        return {
            "document_id": document_id,
            "index_path": str(index_path),
            "metadata_path": str(metadata_path),
            "embedding_model": "all-MiniLM-L6-v2",
            "dimension": dimension,
            "record_count": len(texts)
        }

    def search(
        self,
        document_id: str,
        query: str,
        top_k: int = 5
    ):

        index_path = (
            self.index_dir /
            f"{document_id}_architecture.faiss"
        )

        metadata_path = (
            self.index_dir /
            f"{document_id}_architecture_metadata.json"
        )

        if not index_path.exists():
            raise ArchitectureIndexingError(
                "Architecture FAISS index not found."
            )

        if not metadata_path.exists():
            raise ArchitectureIndexingError(
                "Architecture metadata not found."
            )

        index = faiss.read_index(
            str(index_path)
        )

        with open(
            metadata_path,
            "r",
            encoding="utf-8"
        ) as file:
            metadata = json.load(file)

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        k = min(
            top_k,
            index.ntotal
        )

        scores, indices = index.search(
            query_embedding,
            k
        )

        results = []

        seen = set()

        for score, idx in zip(
    scores[0],
    indices[0]
            ):

            if idx < 0:
                continue

            record = metadata["records"][int(idx)]

    # Create a stable identity for the architecture knowledge.
            if record.get("type") == "architecture_entity":

                key = (
            "entity",
            record.get("entity_type"),
            str(record.get("name", "")).lower()
        )

            elif record.get("type") == "architecture_relationship":

                key = (
            "relationship",
            str(record.get("source", "")).lower(),
            str(record.get("relationship", "")).lower(),
            str(record.get("target", "")).lower()
        )

            else:

                key = (
            record.get("type"),
            record.get("text")
        )

    # Skip duplicate knowledge.
            if key in seen:
                continue

            seen.add(key)

            results.append({
        "score": float(score),
        "type": record.get("type"),
        "entity_type": record.get("entity_type"),
        "name": record.get("name"),
        "source": record.get("source"),
        "relationship": record.get("relationship"),
        "target": record.get("target"),
        "text": record.get("text"),
        "page": record.get("page"),
        "section": record.get("section")
    })

            if len(results) >= top_k:
                 break

            return results