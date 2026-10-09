
import json
import sqlite3

from flask import Blueprint, jsonify, request

from app.auth import token_required
from app.database import get_db


conversations_bp = Blueprint(
    "conversations",
    __name__,
    url_prefix="/api/conversations",
)


def get_owned_conversation(connection, conversation_id, user_id):
    """Return a conversation only when it belongs to this user."""
    return connection.execute(
        """
        SELECT id, user_id, title, created_at, updated_at
        FROM conversations
        WHERE id = ? AND user_id = ?
        """,
        (conversation_id, user_id),
    ).fetchone()


def serialize_message(row):
    """Convert a database message row to a JSON-safe dictionary."""
    try:
        citations = json.loads(row["citations_json"]) if row["citations_json"] else []
    except (json.JSONDecodeError, TypeError):
        citations = []

    return {
        "id": row["id"],
        "conversation_id": row["conversation_id"],
        "role": row["role"],
        "content": row["content"],
        "citations": citations,
        "created_at": row["created_at"],
    }


def serialize_conversation(row, message_count=0):
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "message_count": message_count,
    }


@conversations_bp.route("", methods=["POST"])
@token_required
def create_conversation(user_id):
    payload = request.get_json(silent=True) or {}
    title = payload.get("title", "New conversation")

    if not isinstance(title, str):
        return jsonify({"error": "Title must be a string."}), 400

    title = title.strip() or "New conversation"

    if len(title) > 200:
        return jsonify({"error": "Title cannot exceed 200 characters."}), 400

    connection = get_db()

    try:
        cursor = connection.execute(
            """
            INSERT INTO conversations (user_id, title)
            VALUES (?, ?)
            """,
            (user_id, title),
        )
        conversation_id = cursor.lastrowid
        connection.commit()

        row = get_owned_conversation(
            connection, conversation_id, user_id
        )

        return jsonify({
            "conversation": serialize_conversation(row)
        }), 201

    except sqlite3.Error:
        connection.rollback()
        return jsonify({"error": "Could not create conversation."}), 500

    finally:
        connection.close()


@conversations_bp.route("", methods=["GET"])
@token_required
def list_conversations(user_id):
    connection = get_db()

    try:
        rows = connection.execute(
            """
            SELECT
                c.id,
                c.user_id,
                c.title,
                c.created_at,
                c.updated_at,
                COUNT(m.id) AS message_count
            FROM conversations c
            LEFT JOIN messages m
                ON m.conversation_id = c.id
               AND m.user_id = c.user_id
            WHERE c.user_id = ?
            GROUP BY
                c.id, c.user_id, c.title,
                c.created_at, c.updated_at
            ORDER BY c.updated_at DESC, c.id DESC
            """,
            (user_id,),
        ).fetchall()

        return jsonify({
            "conversations": [
                serialize_conversation(row, row["message_count"])
                for row in rows
            ]
        }), 200

    finally:
        connection.close()


@conversations_bp.route("/<int:conversation_id>", methods=["GET"])
@token_required
def get_conversation(conversation_id, user_id):
    connection = get_db()

    try:
        conversation = get_owned_conversation(
            connection, conversation_id, user_id
        )

        if conversation is None:
            return jsonify({"error": "Conversation not found."}), 404

        rows = connection.execute(
            """
            SELECT id, conversation_id, role, content,
                   citations_json, created_at
            FROM messages
            WHERE conversation_id = ? AND user_id = ?
            ORDER BY id ASC
            """,
            (conversation_id, user_id),
        ).fetchall()

        return jsonify({
            "conversation": serialize_conversation(conversation),
            "messages": [serialize_message(row) for row in rows],
        }), 200

    finally:
        connection.close()


@conversations_bp.route(
    "/<int:conversation_id>/messages",
    methods=["POST"],
)
@token_required
def add_message(conversation_id, user_id):
    payload = request.get_json(silent=True) or {}

    role = payload.get("role")
    content = payload.get("content")
    citations = payload.get("citations", [])

    if role not in ("user", "assistant"):
        return jsonify({
            "error": "Role must be 'user' or 'assistant'."
        }), 400

    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "Message content is required."}), 400

    if not isinstance(citations, list):
        return jsonify({"error": "Citations must be a list."}), 400

    try:
        citations_json = json.dumps(citations)
    except (TypeError, ValueError):
        return jsonify({"error": "Citations must be JSON-serializable."}), 400

    connection = get_db()

    try:
        conversation = get_owned_conversation(
            connection, conversation_id, user_id
        )

        if conversation is None:
            return jsonify({"error": "Conversation not found."}), 404

        cursor = connection.execute(
            """
            INSERT INTO messages (
                conversation_id, user_id, role, content, citations_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                user_id,
                role,
                content.strip(),
                citations_json,
            ),
        )

        # Generate a title from the first user question.
        if (
            role == "user"
            and conversation["title"] == "New conversation"
        ):
            title = " ".join(content.split())[:45]
            if len(" ".join(content.split())) > 45:
                title += "..."

            connection.execute(
                """
                UPDATE conversations
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (title, conversation_id, user_id),
            )
        else:
            connection.execute(
                """
                UPDATE conversations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (conversation_id, user_id),
            )

        connection.commit()

        row = connection.execute(
            """
            SELECT id, conversation_id, role, content,
                   citations_json, created_at
            FROM messages
            WHERE id = ? AND user_id = ?
            """,
            (cursor.lastrowid, user_id),
        ).fetchone()

        return jsonify({
            "message": serialize_message(row)
        }), 201

    except sqlite3.Error:
        connection.rollback()
        return jsonify({"error": "Could not save message."}), 500

    finally:
        connection.close()


@conversations_bp.route("/<int:conversation_id>", methods=["DELETE"])
@token_required
def delete_conversation(conversation_id, user_id):
    connection = get_db()

    try:
        conversation = get_owned_conversation(
            connection, conversation_id, user_id
        )

        if conversation is None:
            return jsonify({"error": "Conversation not found."}), 404

        # Delete explicitly so this also works if SQLite foreign-key
        # enforcement is not enabled on the current connection.
        connection.execute(
            """
            DELETE FROM messages
            WHERE conversation_id = ? AND user_id = ?
            """,
            (conversation_id, user_id),
        )

        connection.execute(
            """
            DELETE FROM conversations
            WHERE id = ? AND user_id = ?
            """,
            (conversation_id, user_id),
        )

        connection.commit()

        return jsonify({"message": "Conversation deleted."}), 200

    except sqlite3.Error:
        connection.rollback()
        return jsonify({"error": "Could not delete conversation."}), 500

    finally:
        connection.close()
