import fitz

from app.chunking_service import (
    generate_chunks_for_text,
    save_chunks,
)
from app.embedding_service import (
    create_embeddings,
    get_embedding_dimension,
    get_embedding_model_name,
    save_embeddings,
)
from app.vectorstore import vectorstore_registry


DEFAULT_CHUNKING_STRATEGY = "fixed"
DEFAULT_EMBEDDING_MODEL = "minilm"


def extract_pages_from_pdf(pdf_path):
    """Extract text while preserving PDF page numbers."""
    pages = []

    with fitz.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page_number": page_number,
                    "text": text,
                })

    if not pages:
        raise ValueError(
            "No extractable text was found in the PDF."
        )

    return pages


def index_document(
    document_id,
    user_id,
    pdf_path,
    strategies=None,
    models=None,
):
    """Build separate FAISS indexes for selected configurations."""
    strategies = strategies or [
        DEFAULT_CHUNKING_STRATEGY
    ]
    models = models or [
        DEFAULT_EMBEDDING_MODEL
    ]

    pages = extract_pages_from_pdf(pdf_path)
    results = []

    for strategy_name in strategies:
        chunks = []

        for page in pages:
            page_chunks = generate_chunks_for_text(
                page["text"],
                strategy_name,
                page["page_number"],
            )
            chunks.extend(page_chunks)

        if not chunks:
            raise ValueError(
                f"No chunks generated for strategy: "
                f"{strategy_name}"
            )

        for index, chunk in enumerate(chunks):
            chunk.chunk_index = index

        # Save this strategy's chunks and retain their SQLite IDs.
        chunk_ids = save_chunks(
            document_id,
            user_id,
            chunks,
        )

        for model_key in models:
            texts = [chunk.text for chunk in chunks]
            vectors = create_embeddings(texts, model_key)

            if len(vectors) != len(chunks):
                raise ValueError(
                    "Embedding count does not match chunk count."
                )

            embedding_path = save_embeddings(
                vectors,
                document_id,
                model_key,
                strategy_name,
            )

            dimension = get_embedding_dimension(model_key)
            model_name = get_embedding_model_name(model_key)

            store, metadata, paths = (
                vectorstore_registry.create(
                    document_id,
                    strategy_name,
                    model_key,
                    dimension,
                )
            )

            store.add_vectors(vectors)

            metadata.add_many([
                {
                    "vector_index": index,
                    "chunk_id": chunk_ids[index],
                    "document_id": document_id,
                    "user_id": user_id,
                    "page_number": chunk.page_number,
                    "section_title": chunk.section_title,
                    "chunking_strategy": strategy_name,
                    "embedding_model": model_key,
                    "embedding_model_name": model_name,
                    "text": chunk.text,
                }
                for index, chunk in enumerate(chunks)
            ])

            vectorstore_registry.save(
                store,
                metadata,
                paths,
            )

            results.append({
                "chunking_strategy": strategy_name,
                "embedding_model": model_key,
                "embedding_model_name": model_name,
                "embedding_dimension": dimension,
                "chunk_count": len(chunks),
                "vector_count": store.size(),
                "embedding_file": embedding_path,
                "faiss_index": paths["index"],
                "metadata_file": paths["metadata"],
            })

    return {
        "document_id": document_id,
        "page_count": len(pages),
        "configurations": results,
    }