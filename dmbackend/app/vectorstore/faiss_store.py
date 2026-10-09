import os

import faiss
import numpy as np


class FAISSStore:
    """
    FAISS vector store using normalized vectors and
    inner-product search for cosine similarity.
    """

    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)

    def add_vectors(self, vectors):
        vectors = np.asarray(vectors, dtype=np.float32)

        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {vectors.shape[1]}."
            )

        # Sentence Transformer embeddings are already normalized,
        # but normalize again to guarantee cosine-search behavior.
        faiss.normalize_L2(vectors)

        self.index.add(vectors)

    def search(self, query_vector, top_k=5):
        query_vector = np.asarray(
            query_vector,
            dtype=np.float32
        )

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        if query_vector.shape[1] != self.dimension:
            raise ValueError(
                f"Query dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {query_vector.shape[1]}."
            )

        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(
            query_vector,
            min(top_k, self.index.ntotal)
        )

        return scores, indices

    def size(self):
        return self.index.ntotal

    def save(self, path):
        directory = os.path.dirname(path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        faiss.write_index(self.index, path)

    @classmethod
    def load(cls, path):
        index = faiss.read_index(path)

        store = cls(index.d)
        store.index = index

        return store