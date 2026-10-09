import os

from app.database import get_db
from app.retrieval_service import search_document
from app.vectorstore import vectorstore_registry


QUESTION = (
    "Explain the layered software architecture "
    "and the responsibilities of its layers."
)


def find_indexed_documents():
    connection = get_db()

    try:
        documents = connection.execute(
            """
            SELECT id, user_id, original_filename
            FROM documents
            WHERE status = 'processed'
            ORDER BY id DESC
            """
        ).fetchall()
    finally:
        connection.close()

    indexed = []

    for document in documents:
        paths = vectorstore_registry.get_paths(
            document["id"],
            "fixed",
            "minilm",
        )

        if (
            os.path.isfile(paths["index"])
            and os.path.isfile(paths["metadata"])
        ):
            indexed.append(document)

    return indexed


print("=" * 70)
print("SEMANTIC RETRIEVAL TEST")
print("=" * 70)
print("Question:", QUESTION)
print()

documents = find_indexed_documents()

if not documents:
    raise SystemExit(
        "No processed documents have a fixed + minilm index."
    )

tested = False

for document in documents:
    print("-" * 70)
    print("Document ID:", document["id"])
    print("Filename:", document["original_filename"])

    try:
        results = search_document(
            document_id=document["id"],
            user_id=document["user_id"],
            question=QUESTION,
            top_k=3,
        )
    except Exception as error:
        print("Retrieval failed:", error)
        continue

    if not results:
        print("No valid results returned.")
        continue

    for rank, result in enumerate(results, start=1):
        print()
        print(f"Result {rank}")
        print("Chunk ID:", result["chunk_id"])
        print("Page:", result["page_number"])
        print("Section:", result["section_title"])
        print("Similarity:", round(
            result["similarity_score"], 4
        ))
        print("Source:", result["filename"])
        print("Text:")
        print(result["text"][:700])

    tested = True

if not tested:
    raise SystemExit(
        "No valid retrieval results. Check the indexing errors above."
    )

print()
print("=" * 70)
print("RETRIEVAL TEST PASSED")
print("=" * 70)