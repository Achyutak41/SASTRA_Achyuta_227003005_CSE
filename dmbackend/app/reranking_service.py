from functools import lru_cache

from sentence_transformers import CrossEncoder


DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=2)
def get_reranker(model_name=DEFAULT_RERANKER_MODEL):
    """
    Load and cache the cross-encoder model.
    The model is loaded only once per model name.
    """
    return CrossEncoder(
        model_name,
        max_length=512,
    )


def rerank_results(question, results, top_k=5):
    """
    Reorder retrieved passages using question-passage relevance.

    Each result must contain a 'text' field.
    Returns the highest-ranked top_k results.
    """
    if not results:
        return []

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must not be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    reranker = get_reranker()

    pairs = [
        (question.strip(), result["text"])
        for result in results
    ]

    scores = reranker.predict(
        pairs,
        batch_size=16,
        show_progress_bar=False,
    )

    ranked_results = []

    for result, score in zip(results, scores):
        ranked_result = result.copy()
        ranked_result["rerank_score"] = float(score)
        ranked_results.append(ranked_result)

    ranked_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return ranked_results[:top_k]