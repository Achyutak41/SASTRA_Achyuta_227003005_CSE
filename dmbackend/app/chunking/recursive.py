from app.chunking.base import Chunk


SEPARATORS = [
    "\n\n",
    "\n",
    ". ",
    " ",
    ""
]


def recursive_split(
    text,
    max_characters
):
    text = text.strip()

    if len(text) <= max_characters:
        return [text]

    for separator in SEPARATORS:

        if separator == "":
            break

        parts = text.split(
            separator
        )

        if len(parts) <= 1:
            continue

        chunks = []

        current = ""

        for part in parts:

            candidate = (
                part
                if not current
                else current
                + separator
                + part
            )

            if (
                len(candidate)
                <= max_characters
            ):
                current = candidate
            else:
                if current.strip():
                    chunks.extend(
                        recursive_split(
                            current,
                            max_characters
                        )
                    )

                current = part

        if current.strip():
            chunks.extend(
                recursive_split(
                    current,
                    max_characters
                )
            )

        return chunks

    result = []

    for start in range(
        0,
        len(text),
        max_characters
    ):
        result.append(
            text[
                start:
                start + max_characters
            ]
        )

    return result


def recursive_chunks(
    text,
    max_characters=1000,
    page_number=None
):
    pieces = recursive_split(
        text,
        max_characters
    )

    chunks = []

    for index, piece in enumerate(
        pieces
    ):
        chunks.append(
            Chunk(
                text=piece,
                page_number=page_number,
                chunk_index=index,
                chunking_strategy="recursive",
                chunk_size=max_characters,
                chunk_overlap=0
            )
        )

    return chunks