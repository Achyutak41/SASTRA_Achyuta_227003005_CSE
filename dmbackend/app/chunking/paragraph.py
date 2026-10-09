from app.chunking.base import Chunk


def split_paragraphs(text):
    paragraphs = text.split(
        "\n\n"
    )

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


def paragraph_chunks(
    text,
    max_characters=2000,
    page_number=None
):
    paragraphs = split_paragraphs(
        text
    )

    chunks = []

    current_parts = []
    current_length = 0

    chunk_index = 0

    for paragraph in paragraphs:

        paragraph_length = len(
            paragraph
        )

        additional_length = (
            paragraph_length
            + (
                2
                if current_parts
                else 0
            )
        )

        if (
            current_parts
            and
            current_length
            + additional_length
            > max_characters
        ):
            chunk_text = "\n\n".join(
                current_parts
            )

            chunks.append(
                Chunk(
                    text=chunk_text,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    chunking_strategy="paragraph",
                    chunk_size=max_characters,
                    chunk_overlap=0
                )
            )

            chunk_index += 1

            current_parts = []
            current_length = 0

        current_parts.append(
            paragraph
        )

        current_length += (
            paragraph_length
            + (
                2
                if len(current_parts) > 1
                else 0
            )
        )

    if current_parts:
        chunk_text = "\n\n".join(
            current_parts
        )

        chunks.append(
            Chunk(
                text=chunk_text,
                page_number=page_number,
                chunk_index=chunk_index,
                chunking_strategy="paragraph",
                chunk_size=max_characters,
                chunk_overlap=0
            )
        )

    return chunks