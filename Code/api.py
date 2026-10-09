import os
import uuid
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    request,
)
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ingestion.pdf_ingestor import (
    HLDDocumentIngestor,
    HLDIngestionError,
)
from ingestion.architecture_extractor import (
    AUTOSARArchitectureExtractor,
    ArchitectureExtractionError,
)
from ingestion.architecture_cleaner import (
    AUTOSARArchitectureCleaner,
    ArchitectureCleaningError
)
# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

app = Flask(__name__)

CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024


# ---------------------------------------------------------
# Directories
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "Input_Data" / "uploads"

PROCESSED_DIR = BASE_DIR / "Input_Data" / "processed"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Ingestor
# ---------------------------------------------------------

ingestor = HLDDocumentIngestor(
    upload_dir=str(UPLOAD_DIR),
    processed_dir=str(PROCESSED_DIR),
)


architecture_extractor = AUTOSARArchitectureExtractor(
    processed_dir=str(PROCESSED_DIR)
)

architecture_cleaner = AUTOSARArchitectureCleaner(
    processed_dir=str(PROCESSED_DIR)
)
# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify(
        {
            "status": "ok",
            "service": "AUTOSAR HLD Ingestion API",
            "checkpoint": 10,
        }
    )


# ---------------------------------------------------------
# Upload HLD
# ---------------------------------------------------------

@app.route("/api/upload-hld", methods=["POST"])
def upload_hld():

    if "file" not in request.files:

        return jsonify(
            {
                "success": False,
                "error": "No file provided."
            }
        ), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:

        return jsonify(
            {
                "success": False,
                "error": "No filename provided."
            }
        ), 400

    original_filename = uploaded_file.filename

    safe_filename = secure_filename(
        original_filename
    )

    if not safe_filename.lower().endswith(".pdf"):

        return jsonify(
            {
                "success": False,
                "error": "Only PDF files are supported."
            }
        ), 400

    # Add UUID to prevent filename collisions.
    unique_filename = (
        f"{uuid.uuid4().hex}_{safe_filename}"
    )

    upload_path = UPLOAD_DIR / unique_filename

    try:

        uploaded_file.save(upload_path)

        result = ingestor.ingest(
            upload_path
        )

        return jsonify(
            {
                "success": True,
                "message": "HLD PDF ingested successfully.",
                "document": result,
            }
        ), 200

    except HLDIngestionError as exc:

        if upload_path.exists():
            upload_path.unlink()

        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 400

    except Exception as exc:

        if upload_path.exists():
            upload_path.unlink()

        return jsonify(
            {
                "success": False,
                "error": f"Unexpected server error: {exc}",
            }
        ), 500

@app.route(
    "/api/extract-architecture",
    methods=["POST", "GET"],
)
def extract_architecture():

    # -----------------------------------------------------
    # Accept document_id from JSON
    # -----------------------------------------------------

    document_id = None

    data = request.get_json(
        silent=True
    )

    if data:
        document_id = data.get(
            "document_id"
        )

    # -----------------------------------------------------
    # Also accept document_id from query parameter
    # -----------------------------------------------------

    if not document_id:
        document_id = request.args.get(
            "document_id"
        )

    # -----------------------------------------------------
    # Validate document ID
    # -----------------------------------------------------

    if not document_id:

        return jsonify(
            {
                "success": False,
                "error": (
                    "document_id is required. "
                    "Provide it as JSON or "
                    "as a query parameter."
                ),
            }
        ), 400

    # -----------------------------------------------------
    # Extract architecture
    # -----------------------------------------------------

    try:

        result = (
            architecture_extractor
            .extract_from_document(
                document_id
            )
        )

        return jsonify(
            {
                "success": True,
                "message": (
                    "AUTOSAR architecture "
                    "knowledge extracted successfully."
                ),
                "architecture": result,
            }
        ), 200

    except ArchitectureExtractionError as exc:

        return jsonify(
            {
                "success": False,
                "error": str(exc),
            }
        ), 400

    except Exception as exc:

        return jsonify(
            {
                "success": False,
                "error": (
                    f"Unexpected server error: {exc}"
                ),
            }
        ), 500


@app.route("/api/clean-architecture", methods=["POST", "GET"])
def clean_architecture():

    document_id = None

    data = request.get_json(silent=True)

    if data:
        document_id = data.get("document_id")

    if not document_id:
        document_id = request.args.get("document_id")

    if not document_id:
        return jsonify({
            "success": False,
            "error": "document_id is required."
        }), 400

    try:

        result = architecture_cleaner.clean_architecture(
            document_id
        )

        return jsonify({
            "success": True,
            "message": "AUTOSAR architecture knowledge cleaned successfully.",
            "architecture": result
        }), 200

    except ArchitectureCleaningError as exc:

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except Exception as exc:

        return jsonify({
            "success": False,
            "error": f"Unexpected error: {exc}"
        }), 500

    
    
# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
    )