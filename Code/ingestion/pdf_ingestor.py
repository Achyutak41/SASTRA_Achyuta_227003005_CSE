import json
import re
import uuid
from pathlib import Path

import pymupdf


class HLDIngestionError(Exception):
    """Raised when HLD PDF ingestion fails."""
    pass


class HLDDocumentIngestor:
    """
    Handles AUTOSAR HLD PDF ingestion.

    Responsibilities:
    - Validate PDF
    - Extract normal PDF text
    - Detect scanned/image-only pages
    - Attempt OCR when available
    - Preserve document/page/section metadata
    - Save structured JSON
    """

    def __init__(
        self,
        upload_dir="Input_Data/uploads",
        processed_dir="Input_Data/processed",
    ):
        self.upload_dir = Path(upload_dir)
        self.processed_dir = Path(processed_dir)

        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.processed_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def ingest(self, file_path):
        """
        Ingest one HLD PDF and return structured metadata.
        """

        file_path = Path(file_path)

        # Validate the uploaded file
        self._validate_file(file_path)

        # Generate unique document ID
        document_id = str(uuid.uuid4())

        try:
            document = pymupdf.open(str(file_path))

        except Exception as exc:
            raise HLDIngestionError(
                f"Unable to open PDF: {exc}"
            ) from exc

        try:

            if document.page_count == 0:
                raise HLDIngestionError(
                    "The PDF contains no pages."
                )

            pages = []

            # Process every page
            for page_index in range(document.page_count):

                page = document.load_page(page_index)

                page_result = self._extract_page(
                    page=page,
                    page_number=page_index + 1,
                    document_name=file_path.name,
                )

                pages.append(page_result)

        finally:
            # Always close the PDF
            document.close()

        # Build final structured document
        result = {
            "document_id": document_id,
            "document_name": file_path.name,
            "page_count": len(pages),
            "ingestion_status": "success",
            "pages": pages,
        }

        # Save processed JSON
        output_file = (
            self.processed_dir
            / f"{document_id}.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                result,
                f,
                indent=2,
                ensure_ascii=False,
            )

        result["processed_file"] = str(
            output_file
        )

        return result

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def _validate_file(self, file_path):
        """
        Validate the uploaded PDF.
        """

        if not file_path.exists():
            raise HLDIngestionError(
                "Uploaded file does not exist."
            )

        if not file_path.is_file():
            raise HLDIngestionError(
                "Uploaded path is not a file."
            )

        if file_path.suffix.lower() != ".pdf":
            raise HLDIngestionError(
                "Only PDF files are supported."
            )

        # 25 MB safety limit for prototype
        max_size = 25 * 1024 * 1024

        if file_path.stat().st_size > max_size:
            raise HLDIngestionError(
                "PDF exceeds the 25 MB upload limit."
            )

    # ---------------------------------------------------------
    # Page extraction
    # ---------------------------------------------------------

    def _extract_page(
        self,
        page,
        page_number,
        document_name,
    ):
        """
        Extract text and metadata from one PDF page.
        """

        text = page.get_text("text").strip()

        extraction_method = "text"

        # A page with very little extracted text
        # may be scanned/image-based.
        if len(text) < 50:

            ocr_text = self._try_ocr(page)

            if ocr_text:

                text = ocr_text

                extraction_method = "ocr"

            elif text:

                extraction_method = (
                    "text_low_content"
                )

            else:

                extraction_method = (
                    "image_only_ocr_unavailable"
                )

        # Detect likely section heading
        section = self._detect_section(text)

        return {
            "document": document_name,
            "page": page_number,
            "section": section,
            "text": text,
            "extraction_method": extraction_method,
            "character_count": len(text),
        }

    # ---------------------------------------------------------
    # OCR
    # ---------------------------------------------------------

    def _try_ocr(self, page):
        """
        Attempt OCR for pages with little/no extracted text.

        Requires:
        - pytesseract
        - Pillow
        - Tesseract OCR installed on the system
        """

        try:

            import pytesseract
            from PIL import Image

            # Render PDF page as an image
            pix = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False,
            )

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples,
            )

            text = pytesseract.image_to_string(
                image
            ).strip()

            return text

        except Exception:
            # OCR is optional.
            #
            # Normal text-based PDFs continue to work
            # even when Tesseract is unavailable.
            return ""

    # ---------------------------------------------------------
    # Section detection
    # ---------------------------------------------------------

    def _detect_section(self, text):
        """
        Detect a likely section heading from the
        beginning of extracted page text.
        """

        if not text:
            return "Unknown"

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        # Look at the first few lines for likely headings
        for line in lines[:10]:

            cleaned = re.sub(
                r"\s+",
                " ",
                line,
            ).strip()

            if self._looks_like_heading(cleaned):

                return cleaned[:200]

        return "Unknown"

    # ---------------------------------------------------------
    # Heading detection
    # ---------------------------------------------------------

    def _looks_like_heading(self, line):
        """
        Determine whether a line looks like
        an HLD/AUTOSAR section heading.
        """

        if len(line) < 3:
            return False

        if len(line) > 120:
            return False

        # Numbered headings:
        #
        # 1 Introduction
        # 2. Software Architecture
        # 3.1 Component Design
        if re.match(
            r"^\d+(\.\d+)*[\s.)-]+.+",
            line,
        ):
            return True

        # Common AUTOSAR/HLD terminology
        keywords = [
            "architecture",
            "software component",
            "component architecture",
            "interface",
            "port",
            "runnable",
            "communication",
            "deployment",
            "system",
            "design",
            "requirements",
            "functional",
        ]

        lower_line = line.lower()

        if any(
            keyword in lower_line
            for keyword in keywords
        ):

            # Avoid treating a long paragraph
            # as a heading.
            if len(line.split()) <= 12:
                return True

        # ALL CAPS short lines are often headings
        if (
            line.upper() == line
            and len(line.split()) <= 10
        ):
            return True

        return False