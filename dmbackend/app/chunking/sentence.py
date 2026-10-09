import re

from app.chunking.base import Chunk


SENTENCE_PATTERN = re.compile(
    r"(?<=[.!?])\s+"
)


def split_sentences(text):
    text = text.strip()

    if not text:
        return []

    sentences = SENTENCE_PATTERN.split(
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def sentence_chunks(
    text,
    sentences_per_chunk=5,
    overlap_sentences=1,
    page_number=None
):
    if sentences_per_chunk <= 0:
        raise ValueError(
            "sentences_per_chunk must be greater than 0."
        )

    if overlap_sentences < 0:
        raise ValueError(
            "overlap_sentences cannot be negative."
        )

    if overlap_sentences >= sentences_per_chunk:
        raise ValueError(
            "overlap_sentences must be smaller than sentences_per_chunk."
        )

    sentences = split_sentences(
        text
    )

    chunks = []

    start = 0
    chunk_index = 0

    while start < len(sentences):

        end = min(
            start + sentences_per_chunk,
            len(sentences)
        )

        chunk_text = " ".join(
            sentences[start:end]
        )

        chunks.append(
            Chunk(
                text=chunk_text,
                page_number=page_number,
                chunk_index=chunk_index,
                chunking_strategy="sentence",
                chunk_size=sentences_per_chunk,
                chunk_overlap=overlap_sentences
            )
        )

        chunk_index += 1

        if end >= len(sentences):
            break

        start = (
            end -
            overlap_sentences
        )

    return chunks