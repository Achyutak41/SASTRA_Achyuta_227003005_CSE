from app.chunking import get_chunking_strategy
from app.database import get_db


DEFAULT_STRATEGIES = [
    "fixed",
    "sentence",
    "paragraph",
    "recursive",
    "structural",
]


def save_chunks(document_id, user_id, chunks):
    """
    Save chunks for one document and one chunking strategy.

    Returns:
        list[int]: SQLite IDs corresponding to the saved chunks.

    Important:
        Only replaces chunks belonging to the selected strategy.
        Chunks produced by other strategies are preserved.
    """
    if not chunks:
        return []

    strategy_names = {
        chunk.chunking_strategy
        for chunk in chunks
    }

    if len(strategy_names) != 1:
        raise ValueError(
            "save_chunks() accepts chunks from exactly one "
            "chunking strategy per call."
        )

    strategy_name = strategy_names.pop()

    connection = get_db()
    chunk_ids = []

    try:
        # Remove the old chunks for this strategy only.
        connection.execute(
            """
            DELETE FROM chunks
            WHERE document_id = ?
              AND user_id = ?
              AND chunking_strategy = ?
            """,
            (
                document_id,
                user_id,
                strategy_name,
            ),
        )

        # Insert the new chunks and collect their SQLite IDs.
        for chunk in chunks:
            cursor = connection.execute(
                """
                INSERT INTO chunks (
                    document_id,
                    user_id,
                    chunk_index,
                    page_number,
                    section_title,
                    chunking_strategy,
                    chunk_size,
                    chunk_overlap,
                    text,
                    character_count,
                    token_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    user_id,
                    chunk.chunk_index,
                    chunk.page_number,
                    chunk.section_title,
                    chunk.chunking_strategy,
                    chunk.chunk_size,
                    chunk.chunk_overlap,
                    chunk.text,
                    chunk.character_count,
                    chunk.token_count,
                ),
            )

            chunk_ids.append(cursor.lastrowid)

        connection.commit()
        return chunk_ids

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def generate_chunks_for_text(
    text,
    strategy_name,
    page_number=None,
):
    """
    Generate chunks using the selected registered strategy.

    Supported strategies:
        fixed, sentence, paragraph, recursive, structural
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")

    if not text.strip():
        return []

    strategy = get_chunking_strategy(strategy_name)

    if strategy_name == "fixed":
        return strategy(
            text,
            chunk_size=1000,
            overlap=150,
            page_number=page_number,
        )

    if strategy_name == "sentence":
        return strategy(
            text,
            sentences_per_chunk=5,
            overlap_sentences=1,
            page_number=page_number,
        )

    if strategy_name == "paragraph":
        return strategy(
            text,
            max_characters=2000,
            page_number=page_number,
        )

    if strategy_name == "recursive":
        return strategy(
            text,
            max_characters=1000,
            page_number=page_number,
        )

    if strategy_name == "structural":
        return strategy(
            text,
            max_characters=1500,
            page_number=page_number,
        )

    raise ValueError(
        f"Unsupported chunking strategy: {strategy_name}"
    )


def generate_all_chunks(pages, strategies=None):
    """
    Generate chunks for each requested strategy.

    Args:
        pages: List of dictionaries containing page_number and text.
        strategies: Strategy names to execute. Defaults to all five.

    Returns:
        A combined list of chunks. Each chunk retains its strategy name.
    """
    if strategies is None:
        strategies = DEFAULT_STRATEGIES

    results = []

    for strategy_name in strategies:
        strategy_chunks = []

        for page in pages:
            if not isinstance(page, dict):
                raise TypeError(
                    "Each page must be a dictionary."
                )

            if "text" not in page or "page_number" not in page:
                raise ValueError(
                    "Each page must contain 'text' and 'page_number'."
                )

            page_chunks = generate_chunks_for_text(
                page["text"],
                strategy_name,
                page["page_number"],
            )

            strategy_chunks.extend(page_chunks)

        # Chunk indexes restart at zero for each strategy.
        for index, chunk in enumerate(strategy_chunks):
            chunk.chunk_index = index

        results.extend(strategy_chunks)

    return results