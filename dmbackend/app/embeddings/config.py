EMBEDDING_MODELS = {
    "minilm": {
        "model_name": (
            "sentence-transformers/"
            "all-MiniLM-L6-v2"
        ),
        "provider": "sentence-transformers",
        "language": "en",
        "description": (
            "Lightweight English "
            "sentence embedding model."
        )
    },

    "mpnet": {
        "model_name": (
            "sentence-transformers/"
            "all-mpnet-base-v2"
        ),
        "provider": "sentence-transformers",
        "language": "en",
        "description": (
            "Higher-capacity English "
            "sentence embedding model."
        )
    },

    "bge": {
        "model_name": (
            "BAAI/bge-base-en-v1.5"
        ),
        "provider": "sentence-transformers",
        "language": "en",
        "description": (
            "Retrieval-oriented English "
            "embedding model."
        )
    },

    "multilingual": {
        "model_name": (
            "sentence-transformers/"
            "paraphrase-multilingual-"
            "MiniLM-L12-v2"
        ),
        "provider": "sentence-transformers",
        "language": "multilingual",
        "description": (
            "Multilingual sentence "
            "embedding model."
        )
    }
}


DEFAULT_EMBEDDING_MODEL = "minilm"