import os
import shutil
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd

class DataManagerError(Exception):
    """Custom exception for data manager errors."""
    pass

def save_data(
    web_data: Optional[Dict[str, Any]],
    pdf_data: Optional[Dict[str, Any]],
    pdf_files: Optional[List[str]],
    output_folder: str
) -> Tuple[str, str]:
    """
    Saves structured data to an Excel file and organizes associated PDF files in a separate folder.

    Args:
        web_data (Optional[Dict[str, Any]]): Structured data extracted from web pages.
        pdf_data (Optional[Dict[str, Any]]): Structured data extracted from PDF files.
        pdf_files (Optional[List[str]]): List of PDF file paths to be copied.
        output_folder (str): Path to the output folder.

    Returns:
        Tuple[str, str]: (Path to the Excel file, Path to the PDF folder)

    Raises:
        DataManagerError: If saving fails.
    """
    if not os.path.isdir(output_folder):
        raise DataManagerError(f"Output folder does not exist: {output_folder}")

    excel_path = os.path.join(output_folder, "extracted_data.xlsx")
    pdf_folder = os.path.join(output_folder, "pdf_files")
    os.makedirs(pdf_folder, exist_ok=True)

    # Prepare data for Excel
    excel_writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')

    # Save web data
    if web_data and 'web_data' in web_data:
        web_content = web_data['web_data']
        if isinstance(web_content, list) and web_content:
            df_web = pd.DataFrame(web_content)
        elif isinstance(web_content, dict):
            df_web = pd.DataFrame([web_content])
        else:
            df_web = pd.DataFrame()
        df_web.to_excel(excel_writer, sheet_name='WebData', index=False)
    else:
        # Create an empty sheet if no web data
        pd.DataFrame().to_excel(excel_writer, sheet_name='WebData', index=False)

    # Save PDF data
    if pdf_data and 'pdf_data' in pdf_data:
        pdf_content = pdf_data['pdf_data']
        if isinstance(pdf_content, list) and pdf_content:
            # Flatten metadata for Excel
            records = []
            for item in pdf_content:
                base = {
                    "file_name": item.get("file_name", ""),
                    "file_path": item.get("file_path", ""),
                    "num_pages": item.get("num_pages", 0),
                    "text": item.get("text", "")
                }
                metadata = item.get("metadata", {})
                # Flatten metadata keys
                for k, v in metadata.items():
                    base[f"meta_{k}"] = v
                records.append(base)
            df_pdf = pd.DataFrame(records)
        else:
            df_pdf = pd.DataFrame()
        df_pdf.to_excel(excel_writer, sheet_name='PDFData', index=False)
    else:
        pd.DataFrame().to_excel(excel_writer, sheet_name='PDFData', index=False)

    excel_writer.close()

    # Copy PDF files to pdf_folder
    if pdf_files:
        for pdf_path in pdf_files:
            if not os.path.isfile(pdf_path):
                continue  # Skip missing files
            dest_path = os.path.join(pdf_folder, os.path.basename(pdf_path))
            try:
                shutil.copy2(pdf_path, dest_path)
            except Exception as e:
                raise DataManagerError(f"Failed to copy PDF file {pdf_path}: {str(e)}")

    return excel_path, pdf_folder