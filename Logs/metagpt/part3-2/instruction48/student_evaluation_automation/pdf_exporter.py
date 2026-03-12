import os
import logging
import pdfkit

class PDFExporter:
    """
    Handles PDF export from a document path (HTML or DOCX converted to HTML).
    Uses pdfkit to generate PDF if Google Docs export is insufficient.
    """

    def __init__(self, wkhtmltopdf_path: str = None):
        """
        Initialize the PDFExporter.

        Args:
            wkhtmltopdf_path (str, optional): Path to the wkhtmltopdf executable. If None, uses default.
        """
        self.logger = logging.getLogger("PDFExporter")
        self.wkhtmltopdf_path = wkhtmltopdf_path
        self.config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path) if wkhtmltopdf_path else None

    def export(self, doc_path: str) -> str:
        """
        Export the given document (HTML file) as a PDF.

        Args:
            doc_path (str): Path to the HTML document to convert.

        Returns:
            str: Path to the generated PDF file.
        """
        if not os.path.exists(doc_path):
            self.logger.error(f"Document path does not exist: {doc_path}")
            raise FileNotFoundError(f"Document path does not exist: {doc_path}")

        # Determine output PDF path
        base_name = os.path.splitext(os.path.basename(doc_path))[0]
        pdf_path = os.path.join(os.path.dirname(doc_path), f"{base_name}.pdf")

        try:
            # Convert HTML to PDF
            pdfkit.from_file(doc_path, pdf_path, configuration=self.config)
            self.logger.info(f"Exported PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            self.logger.error(f"Failed to export PDF from {doc_path}: {e}")
            raise