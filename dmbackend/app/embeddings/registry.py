from app.embeddings.config import (
    EMBEDDING_MODELS,
    DEFAULT_EMBEDDING_MODEL
)

from app.embeddings.sentence_transformer import (
    SentenceTransformerProvider
)


class EmbeddingRegistry:

    def __init__(self):
        self._providers = {}


    def available_models(self):
        return list(
            EMBEDDING_MODELS.keys()
        )


    def get_config(
        self,
        model_key
    ):
        if model_key not in EMBEDDING_MODELS:
            raise ValueError(
                f"Unknown embedding model: "
                f"{model_key}"
            )

        return EMBEDDING_MODELS[
            model_key
        ]


    def get(
        self,
        model_key=None
    ):
        if model_key is None:
            model_key = (
                DEFAULT_EMBEDDING_MODEL
            )

        if model_key not in (
            EMBEDDING_MODELS
        ):
            raise ValueError(
                f"Unknown embedding model: "
                f"{model_key}"
            )

        if model_key not in self._providers:

            config = (
                EMBEDDING_MODELS[
                    model_key
                ]
            )

            self._providers[
                model_key
            ] = (
                SentenceTransformerProvider(
                    config["model_name"]
                )
            )

        return self._providers[
            model_key
        ]


embedding_registry = (
    EmbeddingRegistry()
)