from app.chunking.base import Chunk
from app.chunking.sentence import split_sentences


def semantic_chunks(
    text,
    embedding_function,
    similarity_threshold=0.65,
    page_number=None
):
    """
    Create chunks by grouping semantically
    similar neighboring sentences.

    embedding_function must accept a list
    of sentences and return embeddings.
    """

    sentences = split_sentences(
        text
    )

    if not sentences:
        return []

    if len(sentences) == 1:
        return [
            Chunk(
                text=sentences[0],
                page_number=page_number,
                chunk_index=0,
                chunking_strategy="semantic"
            )
        ]

    embeddings = embedding_function(
        sentences
    )

    chunks = []

    current_sentences = [
        sentences[0]
    ]

    chunk_index = 0

    for index in range(
        1,
        len(sentences)
    ):

        similarity = cosine_similarity(
            embeddings[index - 1],
            embeddings[index]
        )

        if (
            similarity
            >= similarity_threshold
        ):
            current_sentences.append(
                sentences[index]
            )

        else:
            chunks.append(
                Chunk(
                    text=" ".join(
                        current_sentences
                    ),
                    page_number=page_number,
                    chunk_index=chunk_index,
                    chunking_strategy="semantic"
                )
            )

            chunk_index += 1

            current_sentences = [
                sentences[index]
            ]

    if current_sentences:
        chunks.append(
            Chunk(
                text=" ".join(
                    current_sentences
                ),
                page_number=page_number,
                chunk_index=chunk_index,
                chunking_strategy="semantic"
            )
        )

    return chunks


def cosine_similarity(
    vector_a,
    vector_b
):
    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b
        )
    )

    magnitude_a = sum(
        a * a
        for a in vector_a
    ) ** 0.5

    magnitude_b = sum(
        b * b
        for b in vector_b
    ) ** 0.5

    if (
        magnitude_a == 0
        or magnitude_b == 0
    ):
        return 0.0

    return (
        dot_product
        / (
            magnitude_a
            * magnitude_b
        )
    )