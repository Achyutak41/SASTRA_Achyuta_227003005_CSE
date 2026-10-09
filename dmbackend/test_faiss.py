import os

import numpy as np

from app.vectorstore.faiss_store import FAISSStore
from app.vectorstore.metadata_store import MetadataStore


print("=" * 70)
print("FAISS VECTOR STORE TEST")
print("=" * 70)


# ---------------------------------------------------------
# 1. Create sample vectors
# ---------------------------------------------------------

dimension = 384

vectors = np.random.rand(
    5,
    dimension
).astype(np.float32)


print("\nCreating vectors...")
print("Vector shape:", vectors.shape)


# ---------------------------------------------------------
# 2. Create FAISS store
# ---------------------------------------------------------

store = FAISSStore(dimension)

store.add_vectors(vectors)


print("\nFAISS index created.")
print("Dimension:", dimension)
print("Number of vectors:", store.size())


# ---------------------------------------------------------
# 3. Create metadata
# ---------------------------------------------------------

metadata = MetadataStore()

for index in range(5):

    metadata.add({
        "vector_index": index,
        "chunk_id": index + 1,
        "document_id": 1,
        "page_number": index + 1,
        "section_title": f"Test Section {index + 1}",
        "chunking_strategy": "fixed",
        "embedding_model": "minilm"
    })


print("\nMetadata entries:", len(metadata.all()))


# ---------------------------------------------------------
# 4. Search
# ---------------------------------------------------------

query = vectors[0].copy()

scores, indices = store.search(
    query,
    top_k=3
)


print("\nSEARCH RESULTS")
print("-" * 70)

for score, index in zip(
    scores[0],
    indices[0]
):

    item = metadata.get(int(index))

    print(
        f"Vector Index : {index}"
    )

    print(
        f"Score        : {score:.6f}"
    )

    print(
        f"Chunk ID      : {item['chunk_id']}"
    )

    print(
        f"Page         : {item['page_number']}"
    )

    print(
        f"Section      : {item['section_title']}"
    )

    print()


# ---------------------------------------------------------
# 5. Save
# ---------------------------------------------------------

output_dir = "data/vectorstores/test"

os.makedirs(
    output_dir,
    exist_ok=True
)

index_path = os.path.join(
    output_dir,
    "index.faiss"
)

metadata_path = os.path.join(
    output_dir,
    "metadata.json"
)


store.save(index_path)
metadata.save(metadata_path)


print("=" * 70)
print("FILES SAVED")
print("=" * 70)

print("FAISS:", index_path)
print("Metadata:", metadata_path)


# ---------------------------------------------------------
# 6. Load again
# ---------------------------------------------------------

loaded_store = FAISSStore.load(
    index_path
)

loaded_metadata = MetadataStore.load(
    metadata_path
)


print("\nLOADED AGAIN")

print(
    "FAISS vectors:",
    loaded_store.size()
)

print(
    "Metadata entries:",
    len(loaded_metadata.all())
)


# ---------------------------------------------------------
# 7. Final
# ---------------------------------------------------------

if (
    loaded_store.size() == 5
    and len(loaded_metadata.all()) == 5
):
    print("\n" + "=" * 70)
    print("FAISS TEST PASSED")
    print("=" * 70)
else:
    print("\nFAISS TEST FAILED")