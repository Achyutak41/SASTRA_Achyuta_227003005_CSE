import re

from app.chunking.base import Chunk


HEADING_PATTERN = re.compile(
    r"^\s*("
    r"(?:\d+\.)+\d*"
    r"|"
    r"[A-Z][A-Z0-9\s\-]{4,}"
    r")\s+(.+?)\s*$"
)


def is_heading(line):
    line = line.strip()

    if not line:
        return False

    match = HEADING_PATTERN.match(
        line
    )

    return match is not None


def structural_chunks(
    text,
    max_characters=1500,
    page_number=None
):
    lines = text.splitlines()

    sections = []

    current_heading = None
    current_content = []

    for line in lines:

        stripped = line.strip()

        if not stripped:
            continue

        if is_heading(stripped):

            if current_content:
                sections.append(
                    (
                        current_heading,
                        "\n".join(
                            current_content
                        )
                    )
                )

            current_heading = stripped
            current_content = []

        else:
            current_content.append(
                stripped
            )

    if current_content:
        sections.append(
            (
                current_heading,
                "\n".join(
                    current_content
                )
            )
        )

    chunks = []

    chunk_index = 0

    for heading, content in sections:

        if len(content) <= max_characters:

            chunk_text = (
                f"{heading}\n\n"
                f"{content}"
                if heading
                else content
            )

            chunks.append(
                Chunk(
                    text=chunk_text,
                    page_number=page_number,
                    section_title=heading,
                    chunk_index=chunk_index,
                    chunking_strategy="structural",
                    chunk_size=max_characters,
                    chunk_overlap=0
                )
            )

            chunk_index += 1

        else:

            words = content.split()

            current_words = []
            current_length = 0

            for word in words:

                if (
                    current_words
                    and
                    current_length
                    + len(word)
                    + 1
                    > max_characters
                ):
                    chunk_text = (
                        f"{heading}\n\n"
                        if heading
                        else ""
                    )

                    chunk_text += " ".join(
                        current_words
                    )

                    chunks.append(
                        Chunk(
                            text=chunk_text,
                            page_number=page_number,
                            section_title=heading,
                            chunk_index=chunk_index,
                            chunking_strategy="structural",
                            chunk_size=max_characters,
                            chunk_overlap=0
                        )
                    )

                    chunk_index += 1

                    current_words = []
                    current_length = 0

                current_words.append(
                    word
                )

                current_length += (
                    len(word) + 1
                )

            if current_words:

                chunk_text = (
                    f"{heading}\n\n"
                    if heading
                    else ""
                )

                chunk_text += " ".join(
                    current_words
                )

                chunks.append(
                    Chunk(
                        text=chunk_text,
                        page_number=page_number,
                        section_title=heading,
                        chunk_index=chunk_index,
                        chunking_strategy="structural",
                        chunk_size=max_characters,
                        chunk_overlap=0
                    )
                )

                chunk_index += 1

    return chunks