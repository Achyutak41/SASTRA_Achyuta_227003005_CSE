from app.chunking.fixed import (
    fixed_size_chunks
)

from app.chunking.sentence import (
    sentence_chunks
)

from app.chunking.paragraph import (
    paragraph_chunks
)

from app.chunking.recursive import (
    recursive_chunks
)

from app.chunking.structural import (
    structural_chunks
)


CHUNKING_STRATEGIES = {
    "fixed": fixed_size_chunks,
    "sentence": sentence_chunks,
    "paragraph": paragraph_chunks,
    "recursive": recursive_chunks,
    "structural": structural_chunks
}


def get_chunking_strategy(
    strategy_name
):
    if strategy_name not in CHUNKING_STRATEGIES:
        raise ValueError(
            f"Unknown chunking strategy: "
            f"{strategy_name}"
        )

    return CHUNKING_STRATEGIES[
        strategy_name
    ]


def available_chunking_strategies():
    return list(
        CHUNKING_STRATEGIES.keys()
    )