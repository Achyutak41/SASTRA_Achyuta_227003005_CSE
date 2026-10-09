from app.database import get_db
from app.embedding_service import create_embeddings
from app.reranking_service import rerank_results
from app.vectorstore import vectorstore_registry


DEFAULT_CHUNKING_STRATEGY = "fixed"
DEFAULT_EMBEDDING_MODEL = "minilm"


def is_low_value_chunk(text):
    """
    Filter empty chunks, obvious navigation text,
    and very short fragments.
    """
    normalized = " ".join((text or "").lower().split())

    if not normalized:
        return True

    navigation_phrases = (
        "table of contents",
        "list of figures",
        "list of tables",
    )

    if any(phrase in normalized for phrase in navigation_phrases):
        return True

    if len(normalized) < 80:
        return True

    return False


def search_document(
    document_id,
    user_id,
    question,
    top_k=5,
    chunking_strategy=DEFAULT_CHUNKING_STRATEGY,
    embedding_model=DEFAULT_EMBEDDING_MODEL,
):
    """
    Retrieve candidate passages using FAISS, validate them,
    rerank them using a cross-encoder, and return top_k results.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must not be empty.")

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or top_k < 1
    ):
        raise ValueError("top_k must be a positive integer.")

    connection = get_db()

    try:
        # 1. Verify document ownership.
        document = connection.execute(
            """
            SELECT id, user_id, original_filename, status
            FROM documents
            WHERE id = ? AND user_id = ?
            """,
            (document_id, user_id),
        ).fetchone()

        if document is None:
            raise LookupError(
                "Document not found or access denied."
            )

        # 2. Load the index for the selected configuration.
        store, metadata, paths = vectorstore_registry.load(
            document_id,
            chunking_strategy,
            embedding_model,
        )

        if store.size() == 0:
            return []

        # 3. Embed the question with the same model used for indexing.
        query_vectors = create_embeddings(
            [question.strip()],
            embedding_model,
        )

        # 4. Retrieve extra candidates so filtering does not leave
        #    us with too few results.
        candidate_k = min(
            max(top_k * 5, 20),
            store.size(),
        )

        scores, indices = store.search(
            query_vectors[0],
            top_k=candidate_k,
        )

        candidates = []

        # 5. Validate candidates and remove low-value chunks.
        for score, vector_index in zip(scores[0], indices[0]):
            vector_index = int(vector_index)

            if vector_index < 0:
                continue

            item = metadata.get(vector_index)

            if not item:
                continue

            if (
                item.get("document_id") != document_id
                or item.get("user_id") != user_id
                or item.get("chunking_strategy") != chunking_strategy
                or item.get("embedding_model") != embedding_model
            ):
                continue

            chunk = connection.execute(
                """
                SELECT
                    c.id,
                    c.text,
                    c.page_number,
                    c.section_title,
                    c.chunking_strategy,
                    d.original_filename
                FROM chunks AS c
                JOIN documents AS d
                  ON d.id = c.document_id
                WHERE c.id = ?
                  AND c.document_id = ?
                  AND c.user_id = ?
                  AND d.user_id = ?
                  AND c.chunking_strategy = ?
                """,
                (
                    item.get("chunk_id"),
                    document_id,
                    user_id,
                    user_id,
                    chunking_strategy,
                ),
            ).fetchone()

            if chunk is None:
                continue

            if is_low_value_chunk(chunk["text"]):
                continue

            candidates.append({
                "document_id": document_id,
                "filename": chunk["original_filename"],
                "chunk_id": chunk["id"],
                "text": chunk["text"],
                "page_number": chunk["page_number"],
                "section_title": chunk["section_title"],
                "chunking_strategy": chunk["chunking_strategy"],
                "embedding_model": embedding_model,
                "similarity_score": float(score),
            })

        # 6. Rerank all valid candidates by question-passage relevance.
        #    Return only the requested number of results.
        return rerank_results(
            question=question,
            results=candidates,
            top_k=top_k,
        )

    finally:
        connection.close()