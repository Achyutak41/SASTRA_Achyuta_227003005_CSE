# AUTOSAR HLD PDF Ingestion

## Checkpoint

Checkpoint 10

## Purpose

The system accepts a user-provided AUTOSAR High-Level Design
PDF through a Flask REST API.

## Workflow

User PDF
→ Flask API
→ PDF validation
→ PyMuPDF extraction
→ scanned-page detection
→ OCR when required
→ page/section metadata
→ structured JSON

## API

### Health

GET /api/health

### Upload

POST /api/upload-hld

Form field:

file

## Metadata

Each extracted page preserves:

- document name
- page number
- detected section
- extracted text
- extraction method
- character count

## Security Considerations

- Only PDF extensions are accepted.
- Uploaded filenames are sanitized.
- Upload size is limited to 25 MB.
- Uploaded documents are excluded from Git.
- Processing is performed locally.

## Current Limitation

The extracted document has not yet been connected to the
document-specific FAISS/RAG pipeline.

That integration will be implemented in a subsequent checkpoint.