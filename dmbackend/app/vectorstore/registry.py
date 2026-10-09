import os

from app.vectorstore.config import VECTORSTORE_BASE_DIR
from app.vectorstore.faiss_store import FAISSStore
from app.vectorstore.metadata_store import MetadataStore


class VectorStoreRegistry:

    def __init__(self, base_dir=VECTORSTORE_BASE_DIR):
        self.base_dir = base_dir

    def build_store_name(
        self,
        document_id,
        chunking_strategy,
        embedding_model
    ):
        return (
            f"document_{document_id}"
            f"__{chunking_strategy}"
            f"__{embedding_model}"
        )

    def get_paths(
        self,
        document_id,
        chunking_strategy,
        embedding_model
    ):
        store_name = self.build_store_name(
            document_id,
            chunking_strategy,
            embedding_model
        )

        directory = os.path.join(
            self.base_dir,
            store_name
        )

        return {
            "directory": directory,
            "index": os.path.join(
                directory,
                "index.faiss"
            ),
            "metadata": os.path.join(
                directory,
                "metadata.json"
            )
        }

    def create(
        self,
        document_id,
        chunking_strategy,
        embedding_model,
        dimension
    ):
        paths = self.get_paths(
            document_id,
            chunking_strategy,
            embedding_model
        )

        os.makedirs(
            paths["directory"],
            exist_ok=True
        )

        store = FAISSStore(dimension)
        metadata = MetadataStore()

        return store, metadata, paths

    def save(
        self,
        store,
        metadata,
        paths
    ):
        store.save(paths["index"])
        metadata.save(paths["metadata"])

    def load(
        self,
        document_id,
        chunking_strategy,
        embedding_model
    ):
        paths = self.get_paths(
            document_id,
            chunking_strategy,
            embedding_model
        )

        if not os.path.exists(paths["index"]):
            raise FileNotFoundError(
                f"FAISS index not found: {paths['index']}"
            )

        if not os.path.exists(paths["metadata"]):
            raise FileNotFoundError(
                f"Metadata not found: {paths['metadata']}"
            )

        store = FAISSStore.load(paths["index"])
        metadata = MetadataStore.load(paths["metadata"])

        return store, metadata, paths


vectorstore_registry = VectorStoreRegistry()