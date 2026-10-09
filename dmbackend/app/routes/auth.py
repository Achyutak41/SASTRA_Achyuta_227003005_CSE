from flask import (
    Blueprint,
    jsonify,
    request
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from app.auth import (
    create_access_token,
    token_required
)

from app.database import get_db


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


def serialize_user(user):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"]
    }


@auth_bp.post("/register")
def register():

    data = request.get_json(
        silent=True
    ) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name:
        return jsonify({
            "error": "Name is required."
        }), 400

    if not email:
        return jsonify({
            "error": "Email is required."
        }), 400

    if not password:
        return jsonify({
            "error": "Password is required."
        }), 400

    if len(password) < 6:
        return jsonify({
            "error": "Password must contain at least 6 characters."
        }), 400

    connection = get_db()

    try:
        existing_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:
            return jsonify({
                "error": "An account with this email already exists."
            }), 409

        password_hash = generate_password_hash(
            password
        )

        cursor = connection.execute(
            """
            INSERT INTO users (
                name,
                email,
                password_hash
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password_hash
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        user = connection.execute(
            """
            SELECT
                id,
                name,
                email,
                created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        token = create_access_token(
            user_id
        )

        return jsonify({
            "message": "Registration successful.",
            "user": serialize_user(user),
            "token": token
        }), 201

    finally:
        connection.close()


@auth_bp.post("/login")
def login():

    data = request.get_json(
        silent=True
    ) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    connection = get_db()

    try:
        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if not user:
            return jsonify({
                "error": "Invalid email or password."
            }), 401

        password_valid = check_password_hash(
            user["password_hash"],
            password
        )

        if not password_valid:
            return jsonify({
                "error": "Invalid email or password."
            }), 401

        token = create_access_token(
            user["id"]
        )

        return jsonify({
            "message": "Login successful.",
            "user": serialize_user(user),
            "token": token
        }), 200

    finally:
        connection.close()


@auth_bp.get("/me")
@token_required
def get_current_user(user_id):

    connection = get_db()

    try:
        user = connection.execute(
            """
            SELECT
                id,
                name,
                email,
                created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        if not user:
            return jsonify({
                "error": "User not found."
            }), 404

        return jsonify({
            "user": serialize_user(user)
        }), 200

    finally:
        connection.close()


@auth_bp.post("/logout")
@token_required
def logout(user_id):

    return jsonify({
        "message": "Logout successful."
    }), 200