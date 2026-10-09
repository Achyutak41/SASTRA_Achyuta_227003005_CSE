
from flask import Blueprint, jsonify, request

from app.auth import token_required
from app.ollama_service import OllamaError
from app.rag_service import answer_question


chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/api/chat",
)


def authenticated_user_id(current_user):
    """Extract the ID from a dictionary, row, or user object."""
    if isinstance(current_user, dict):
        user_id = current_user.get("id")
    else:
        try:
            user_id = current_user["id"]
        except (TypeError, KeyError, IndexError):
            user_id = getattr(current_user, "id", None)

    if user_id is None:
        raise ValueError("Authenticated user ID is unavailable.")

    return user_id


@chat_bp.route("/ask", methods=["POST"])
@token_required
def ask_question(user_id):
    payload = request.get_json(silent=True) or {}

    question = payload.get("question")
    document_id = payload.get("document_id")
    top_k = payload.get("top_k", 5)
    chunking_strategy = payload.get("chunking_strategy", "fixed")
    embedding_model = payload.get("embedding_model", "minilm")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "A non-empty question is required."
        }), 400

    try:
        document_id = int(document_id)
        if document_id < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({
            "error": "document_id must be a positive integer."
        }), 400

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or not 1 <= top_k <= 10
    ):
        return jsonify({
            "error": "top_k must be an integer from 1 to 10."
        }), 400

    if not isinstance(chunking_strategy, str):
        return jsonify({
            "error": "chunking_strategy must be a string."
        }), 400

    if not isinstance(embedding_model, str):
        return jsonify({
            "error": "embedding_model must be a string."
        }), 400

    try:

        result = answer_question(
            document_id=document_id,
            user_id=user_id,
            question=question,
            top_k=top_k,
            chunking_strategy=chunking_strategy,
            embedding_model=embedding_model,
        )

        return jsonify(result), 200

    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    except FileNotFoundError:
        return jsonify({
            "error": (
                "The document index was not found. "
                "Check that this document has been indexed "
                "using the selected chunking and embedding settings."
            )
        }), 409

    except OllamaError as exc:
        return jsonify({
            "error": "Answer generation failed.",
            "details": str(exc),
        }), 502
