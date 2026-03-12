import os
import csv
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from PIL import Image

from utils.config import Config

class ExportService:
    def __init__(self, config: Config):
        self.config = config

    def export_to_pdf(self, entries: List[Dict[str, Any]], pdf_path: str, template: str = "Default") -> str:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        y = height - 40
        c.setFont("Helvetica-Bold", 18)
        c.drawString(40, y, "Digital Diver's Logbook")
        y -= 30
        c.setFont("Helvetica", 12)
        c.drawString(40, y, f"Exported: {self.config.get_now_str()}")
        y -= 30

        for entry in entries:
            if y < 120:
                c.showPage()
                y = height - 40
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.darkblue)
            c.drawString(40, y, f"Dive on {entry['date']} at {entry['location']}")
            y -= 20
            c.setFont("Helvetica", 12)
            c.setFillColor(colors.black)
            c.drawString(60, y, f"Depth: {entry['depth']} m, Duration: {entry['duration']} min, Buddy: {entry.get('buddy', '')}")
            y -= 18
            c.drawString(60, y, f"Notes: {entry.get('notes', '')}")
            y -= 18
            c.drawString(60, y, f"Validation: {entry.get('validation_status', 'Pending')}")
            y -= 18
            # Add photo if exists
            if entry.get('photo_path') and os.path.exists(entry['photo_path']):
                try:
                    img = Image.open(entry['photo_path'])
                    img.thumbnail((120, 120))
                    img_path = entry['photo_path']
                    c.drawImage(ImageReader(img), 400, y-10, width=80, height=80)
                    y -= 90
                except Exception:
                    y -= 10
            else:
                y -= 10
            y -= 10
            c.line(40, y, width - 40, y)
            y -= 10
        c.save()
        return pdf_path

    def export_to_csv(self, entries: List[Dict[str, Any]], csv_path: str) -> str:
        fieldnames = [
            "id", "date", "location", "depth", "duration", "buddy", "notes",
            "photo_path", "signature_path", "validation_status", "created_at", "updated_at"
        ]
        with open(csv_path, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in entries:
                writer.writerow({k: entry.get(k, "") for k in fieldnames})
        return csv_path

    def export_to_image(self, entries: List[Dict[str, Any]], image_path: str, template: str = "Default") -> str:
        # Export the first entry as an image summary (for sharing)
        if not entries:
            raise ValueError("No entries to export as image.")
        entry = entries[0]
        width, height = 600, 400
        img = Image.new("RGB", (width, height), color=(240, 250, 255))
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font_title = ImageFont.truetype("arial.ttf", 24)
            font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font_title = None
            font = None
        y = 20
        draw.text((20, y), "Digital Diver's Logbook", fill=(0, 80, 180), font=font_title)
        y += 40
        draw.text((20, y), f"Date: {entry['date']}", fill=(0, 0, 0), font=font)
        y += 25
        draw.text((20, y), f"Location: {entry['location']}", fill=(0, 0, 0), font=font)
        y += 25
        draw.text((20, y), f"Depth: {entry['depth']} m", fill=(0, 0, 0), font=font)
        y += 25
        draw.text((20, y), f"Duration: {entry['duration']} min", fill=(0, 0, 0), font=font)
        y += 25
        draw.text((20, y), f"Buddy: {entry.get('buddy', '')}", fill=(0, 0, 0), font=font)
        y += 25
        draw.text((20, y), f"Notes: {entry.get('notes', '')}", fill=(0, 0, 0), font=font)
        y += 25
        draw.text((20, y), f"Validation: {entry.get('validation_status', 'Pending')}", fill=(0, 0, 0), font=font)
        # Add photo if exists
        if entry.get('photo_path') and os.path.exists(entry['photo_path']):
            try:
                photo = Image.open(entry['photo_path'])
                photo.thumbnail((120, 120))
                img.paste(photo, (400, 40))
            except Exception:
                pass
        img.save(image_path)
        return image_path

    def export_data(self,
                    as_pdf: bool,
                    as_csv: bool,
                    as_image: bool,
                    template: str,
                    to_gdrive: bool,
                    to_dropbox: bool,
                    to_s3: bool,
                    to_local: bool,
                    entries: Optional[List[Dict[str, Any]]] = None,
                    user_id: Optional[int] = None,
                    logbook=None,
                    cloud_service=None) -> Dict[str, str]:
        """
        Export logbook data in selected formats and upload/share as requested.
        Returns a dict of format: { 'pdf': path, 'csv': path, 'image': path }
        """
        if entries is None and logbook and user_id:
            entries = [e.to_dict() for e in logbook.list_entries(user_id)]
        if not entries:
            raise ValueError("No entries to export.")

        output = {}
        base_dir = self.config.get_export_dir()
        os.makedirs(base_dir, exist_ok=True)
        if as_pdf:
            pdf_path = os.path.join(base_dir, f"logbook_export_{user_id or 'user'}.pdf")
            self.export_to_pdf(entries, pdf_path, template)
            output['pdf'] = pdf_path
        if as_csv:
            csv_path = os.path.join(base_dir, f"logbook_export_{user_id or 'user'}.csv")
            self.export_to_csv(entries, csv_path)
            output['csv'] = csv_path
        if as_image:
            image_path = os.path.join(base_dir, f"logbook_export_{user_id or 'user'}.png")
            self.export_to_image(entries, image_path, template)
            output['image'] = image_path

        # Cloud upload
        if cloud_service:
            if to_gdrive and 'pdf' in output:
                cloud_service.upload_to_gdrive(output['pdf'])
            if to_dropbox and 'pdf' in output:
                cloud_service.upload_to_dropbox(output['pdf'], f"/logbook_export_{user_id or 'user'}.pdf")
            if to_s3 and 'pdf' in output:
                bucket = self.config.get('s3_bucket')
                if bucket:
                    cloud_service.upload_to_s3(output['pdf'], bucket, f"logbook_export_{user_id or 'user'}.pdf")
        return output

    def share_via_email(self, as_pdf: bool, as_csv: bool, as_image: bool, template: str,
                        entries: Optional[List[Dict[str, Any]]] = None,
                        user_id: Optional[int] = None,
                        logbook=None):
        # Platform-specific: open email client with attachment(s)
        # Here, just export and print the file paths
        output = self.export_data(as_pdf, as_csv, as_image, template, False, False, False, True, entries, user_id, logbook)
        print("Share via email:", output)
        # Actual implementation would use platform APIs to open email client

    def share_via_apps(self, as_pdf: bool, as_csv: bool, as_image: bool, template: str,
                       entries: Optional[List[Dict[str, Any]]] = None,
                       user_id: Optional[int] = None,
                       logbook=None):
        # Platform-specific: open share dialog with attachment(s)
        output = self.export_data(as_pdf, as_csv, as_image, template, False, False, False, True, entries, user_id, logbook)
        print("Share via apps:", output)
        # Actual implementation would use platform APIs to open share dialog