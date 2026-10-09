import os

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.auth import token_required
from app.database import get_db
from app.document_service import (
    delete_document_files,
    extract_pdf_text,
    save_pdf,
)
from app.indexing_service import index_document


documents_bp = Blueprint(
    "documents",
    __name__,
    url_prefix="/api/documents",
)

ALLOWED_EXTENSION = ".pdf"


def serialize_document(document):
    return {
        "id": document["id"],
        "original_filename": document["original_filename"],
        "file_size": document["file_size"],
        "page_count": document["page_count"],
        "extracted_text_length": document["extracted_text_length"],
        "status": document["status"],
        "error_message": document["error_message"],
        "created_at": document["created_at"],
        "updated_at": document["updated_at"],
    }


@documents_bp.post("/upload")
@token_required
def upload_document(user_id):
    if "file" not in request.files:
        return jsonify({
            "error": "No PDF file was provided."
        }), 400

    file = request.files["file"]

    if not file or not file.filename:
        return jsonify({
            "error": "No PDF file was selected."
        }), 400

    original_filename = secure_filename(file.filename)

    if not original_filename:
        return jsonify({
            "error": "Invalid filename."
        }), 400

    extension = os.path.splitext(original_filename)[1].lower()

    if extension != ALLOWED_EXTENSION:
        return jsonify({
            "error": "Only PDF files are allowed."
        }), 400

    connection = get_db()
    storage_path = None
    extracted_text_path = None
    document_id = None

    try:
        stored_filename, storage_path = save_pdf(file)
        file_size = os.path.getsize(storage_path)

        # Step 1: Extract the PDF text.
        try:
            extraction = extract_pdf_text(
                storage_path,
                stored_filename,
            )

            extracted_text_path = extraction[
                "extracted_text_path"
            ]
            page_count = extraction["page_count"]
            extracted_text_length = extraction[
                "extracted_text_length"
            ]

        except Exception as extraction_error:
            cursor = connection.execute(
                """
                INSERT INTO documents (
                    user_id,
                    original_filename,
                    stored_filename,
                    storage_path,
                    extracted_text_path,
                    file_size,
                    page_count,
                    extracted_text_length,
                    status,
                    error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    original_filename,
                    stored_filename,
                    storage_path,
                    None,
                    file_size,
                    0,
                    0,
                    "failed",
                    str(extraction_error),
                ),
            )

            connection.commit()
            document_id = cursor.lastrowid

            document = connection.execute(
                """
                SELECT *
                FROM documents
                WHERE id = ? AND user_id = ?
                """,
                (document_id, user_id),
            ).fetchone()

            return jsonify({
                "error": "PDF uploaded, but text extraction failed.",
                "document": serialize_document(document),
            }), 422

        # Step 2: Record the extracted document before indexing.
        cursor = connection.execute(
            """
            INSERT INTO documents (
                user_id,
                original_filename,
                stored_filename,
                storage_path,
                extracted_text_path,
                file_size,
                page_count,
                extracted_text_length,
                status,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                original_filename,
                stored_filename,
                storage_path,
                extracted_text_path,
                file_size,
                page_count,
                extracted_text_length,
                "indexing",
                None,
            ),
        )

        connection.commit()
        document_id = cursor.lastrowid

        # Step 3: Build the default FAISS index.
        # Keep the PDF if indexing fails so it can be retried.
        try:
            indexing_result = index_document(
                document_id=document_id,
                user_id=user_id,
                pdf_path=storage_path,
                strategies=["fixed"],
                models=["minilm"],
            )

            connection.execute(
                """
                UPDATE documents
                SET status = ?, error_message = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                ("processed", document_id, user_id),
            )
            connection.commit()

            message = (
                "PDF uploaded, extracted, and indexed successfully."
            )
            indexing_error = None

        except Exception as indexing_exception:
            connection.execute(
                """
                UPDATE documents
                SET status = ?, error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (
                    "indexing_failed",
                    str(indexing_exception),
                    document_id,
                    user_id,
                ),
            )
            connection.commit()

            indexing_result = None
            indexing_error = str(indexing_exception)
            message = (
                "PDF uploaded and extracted, but indexing failed. "
                "The document has been retained for troubleshooting."
            )

        document = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE id = ? AND user_id = ?
            """,
            (document_id, user_id),
        ).fetchone()

        response = {
            "message": message,
            "document": serialize_document(document),
        }

        if indexing_result is not None:
            response["indexing"] = indexing_result

        if indexing_error is not None:
            response["indexing_error"] = indexing_error

        return jsonify(response), 201

    except Exception as error:
        connection.rollback()

        # Only remove files if a document record was never created.
        if document_id is None and storage_path:
            delete_document_files(
                storage_path,
                extracted_text_path,
            )

        return jsonify({
            "error": str(error)
        }), 500

    finally:
        connection.close()


@documents_bp.get("")
@token_required
def list_documents(user_id):
    connection = get_db()

    try:
        documents = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()

        return jsonify({
            "documents": [
                serialize_document(document)
                for document in documents
            ]
        }), 200

    finally:
        connection.close()


@documents_bp.get("/<int:document_id>")
@token_required
def get_document(document_id, user_id):
    connection = get_db()

    try:
        document = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE id = ? AND user_id = ?
            """,
            (document_id, user_id),
        ).fetchone()

        if not document:
            return jsonify({
                "error": "Document not found."
            }), 404

        return jsonify({
            "document": serialize_document(document)
        }), 200

    finally:
        connection.close()


@documents_bp.delete("/<int:document_id>")
@token_required
def delete_document(document_id, user_id):
    connection = get_db()

    try:
        document = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE id = ? AND user_id = ?
            """,
            (document_id, user_id),
        ).fetchone()

        if not document:
            return jsonify({
                "error": "Document not found."
            }), 404

        # Remove the database record first. The chunks table has
        # cascading foreign keys when SQLite foreign keys are enabled.
        connection.execute(
            """
            DELETE FROM documents
            WHERE id = ? AND user_id = ?
            """,
            (document_id, user_id),
        )
        connection.commit()

        delete_document_files(
            document["storage_path"],
            document["extracted_text_path"],
        )

        return jsonify({
            "message": "Document deleted successfully."
        }), 200

    finally:
        connection.close()