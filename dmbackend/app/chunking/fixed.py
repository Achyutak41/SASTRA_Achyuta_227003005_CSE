from app.chunking.base import Chunk


def fixed_size_chunks(
    text,
    chunk_size=1000,
    overlap=150,
    page_number=None
):
    text = text.strip()

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    chunks = []

    start = 0
    chunk_index = 0

    while start < len(text):
        end = min(
            start + chunk_size,
            len(text)
        )

        chunk_text = text[
            start:end
        ].strip()

        if chunk_text:
            chunks.append(
                Chunk(
                    text=chunk_text,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    chunking_strategy="fixed",
                    chunk_size=chunk_size,
                    chunk_overlap=overlap
                )
            )

            chunk_index += 1

        if end >= len(text):
            break

        start = end - overlap

    return chunks