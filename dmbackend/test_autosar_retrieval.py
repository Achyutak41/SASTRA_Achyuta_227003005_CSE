from app.database import get_db
from app.retrieval_service import search_document

QUESTION = (
    "What are the responsibilities of the software "
    "layers in the AUTOSAR layered software architecture?"
)

connection = get_db()

try:
    document = connection.execute(
        """
        SELECT id, user_id, original_filename
        FROM documents
        WHERE original_filename =
            'AUTOSAR_EXP_LayeredSoftwareArchitecture.pdf'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
finally:
    connection.close()

if document is None:
    raise SystemExit("AUTOSAR PDF not found in the database.")

results = search_document(
    document_id=document["id"],
    user_id=document["user_id"],
    question=QUESTION,
    top_k=5,
)

print("Question:", QUESTION)
print("Document:", document["original_filename"])
print("=" * 70)

for rank, result in enumerate(results, start=1):
    print(f"\nResult {rank}")
    print("Page:", result["page_number"])
    print("Score:", round(result["similarity_score"], 4))
    print("Text length:", len(result["text"]))
    print("Text:", result["text"][:1000])
    print("-" * 70)

if not results:
    raise SystemExit("No retrieval results returned.")

print("\nTARGETED RETRIEVAL TEST PASSED")
for index, result in enumerate(results, start=1):
    print(f"\nResult {index}")
    print(f"Page: {result['page_number']}")
    print(
        f"Similarity score: "
        f"{result['similarity_score']:.4f}"
    )
    print(
        f"Rerank score: "
        f"{result.get('rerank_score', 'MISSING')}"
    )
    print(f"Text length: {len(result['text'])}")
    print(f"Text: {result['text'][:1200]}")
    print("-" * 70)