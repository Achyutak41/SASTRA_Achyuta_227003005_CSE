from sentence_transformers import (
    SentenceTransformer
)

from app.embeddings.base import (
    EmbeddingProvider
)


class SentenceTransformerProvider(
    EmbeddingProvider
):

    def __init__(
        self,
        model_name
    ):
        self._model_name = model_name

        self._model = (
            SentenceTransformer(
                model_name
            )
        )


    def encode(
        self,
        texts
    ):
        if isinstance(
            texts,
            str
        ):
            texts = [texts]

        embeddings = (
            self._model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False
            )
        )

        return embeddings


    def dimension(self):
        return (
            self._model
            .get_sentence_embedding_dimension()
        )


    def model_name(self):
        return self._model_name