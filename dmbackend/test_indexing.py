from app.database import get_db
from app.indexing_service import index_document


connection = get_db()

try:
    document = connection.execute(
        """
        SELECT id, user_id, storage_path, original_filename
        FROM documents
        WHERE status = 'processed'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
finally:
    connection.close()


if document is None:
    raise SystemExit(
        "No processed PDF found. Upload a PDF first."
    )


document_id = document["id"]
user_id = document["user_id"]
pdf_path = document["storage_path"]

print("=" * 65)
print("AUTOSAR DOCUMENT INDEXING TEST")
print("=" * 65)
print("Document ID:", document_id)
print("Filename:", document["original_filename"])
print("Configuration: fixed + minilm")
print()

result = index_document(
    document_id=document_id,
    user_id=user_id,
    pdf_path=pdf_path,
    strategies=["fixed"],
    models=["minilm"],
)

print("INDEXING RESULT")
print("-" * 65)
print("Pages:", result["page_count"])

for configuration in result["configurations"]:
    print("Strategy:", configuration["chunking_strategy"])
    print("Model:", configuration["embedding_model"])
    print("Dimension:", configuration["embedding_dimension"])
    print("Chunks:", configuration["chunk_count"])
    print("Vectors:", configuration["vector_count"])
    print("FAISS index:", configuration["faiss_index"])
    print("Metadata:", configuration["metadata_file"])

    assert (
        configuration["chunk_count"]
        == configuration["vector_count"]
    ), "Chunk/vector count mismatch"

print()
print("INDEXING TEST PASSED")