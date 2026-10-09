from app.embeddings import (
    embedding_registry
)


TEST_TEXTS = [
    (
        "AUTOSAR is a standardized "
        "software architecture for "
        "automotive systems."
    ),
    (
        "The Runtime Environment "
        "provides communication between "
        "software components."
    ),
    (
        "The Basic Software provides "
        "services to the application "
        "layer."
    )
]


models = (
    embedding_registry
    .available_models()
)


print()
print("=" * 70)
print("AVAILABLE EMBEDDING MODELS")
print("=" * 70)

for model in models:
    print(
        f"- {model}"
    )


for model_key in models:

    print()
    print("=" * 70)
    print(
        f"MODEL: {model_key}"
    )
    print("=" * 70)

    provider = (
        embedding_registry.get(
            model_key
        )
    )

    print(
        "Model name:",
        provider.model_name()
    )

    print(
        "Dimension:",
        provider.dimension()
    )

    vectors = provider.encode(
        TEST_TEXTS
    )

    print(
        "Vector shape:",
        vectors.shape
    )

    print(
        "Vector type:",
        vectors.dtype
    )

    print(
        "First vector first 5 values:"
    )

    print(
        vectors[0][:5]
    )