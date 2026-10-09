from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt

from flask import (
    current_app,
    jsonify,
    request
)


def create_access_token(user_id):
    now = datetime.now(timezone.utc)

    payload = {
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(
            hours=24
        )
    }

    token = jwt.encode(
        payload,
        current_app.config[
            "JWT_SECRET_KEY"
        ],
        algorithm="HS256"
    )

    return token


def decode_access_token(token):
    try:
        payload = jwt.decode(
            token,
            current_app.config[
                "JWT_SECRET_KEY"
            ],
            algorithms=["HS256"]
        )

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None


def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):

        authorization_header = request.headers.get(
            "Authorization"
        )

        if not authorization_header:
            return jsonify({
                "error": "Authorization token is required."
            }), 401

        parts = authorization_header.split(
            " ",
            1
        )

        if (
            len(parts) != 2
            or parts[0].lower() != "bearer"
        ):
            return jsonify({
                "error": "Invalid authorization format."
            }), 401

        token = parts[1]

        payload = decode_access_token(
            token
        )

        if not payload:
            return jsonify({
                "error": "Invalid or expired token."
            }), 401

        return function(
            *args,
            user_id=payload["user_id"],
            **kwargs
        )

    return decorated