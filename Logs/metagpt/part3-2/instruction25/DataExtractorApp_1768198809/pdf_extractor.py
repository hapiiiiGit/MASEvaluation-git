import os
from typing import List, Dict, Any
import PyPDF2

class PDFExtractorError(Exception):
    """Custom exception for PDF extraction errors."""
    pass

def extract_data(pdf_paths: List[str]) -> Dict[str, Any]:
    """
    Extracts structured data from a list of local PDF files.

    Args:
        pdf_paths (List[str]): List of PDF file paths.

    Returns:
        Dict[str, Any]: Structured data suitable for Excel export.
            Example:
            {
                "pdf_data": [
                    {
                        "file_name": "document1.pdf",
                        "file_path": "/path/to/document1.pdf",
                        "num_pages": 3,
                        "text": "Extracted text from all pages...",
                        "metadata": {
                            "author": "...",
                            "title": "...",
                            ...
                        }
                    },
                    ...
                ]
            }

    Raises:
        PDFExtractorError: If extraction fails for any file.
    """
    pdf_data = []
    for pdf_path in pdf_paths:
        if not os.path.isfile(pdf_path):
            raise PDFExtractorError(f"File not found: {pdf_path}")

        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                # Extract metadata if available
                metadata = {}
                if reader.metadata:
                    for key, value in reader.metadata.items():
                        # PyPDF2 returns keys like '/Author', '/Title'
                        clean_key = key.lstrip('/')
                        metadata[clean_key] = value

                pdf_data.append({
                    "file_name": os.path.basename(pdf_path),
                    "file_path": pdf_path,
                    "num_pages": num_pages,
                    "text": text.strip(),
                    "metadata": metadata
                })
        except Exception as e:
            raise PDFExtractorError(f"Failed to extract {pdf_path}: {str(e)}")

    return {"pdf_data": pdf_data}