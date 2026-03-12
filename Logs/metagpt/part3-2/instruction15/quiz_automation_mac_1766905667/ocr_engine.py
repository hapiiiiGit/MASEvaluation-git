import pytesseract
from PIL import Image
from typing import Optional


class OCREngine:
    """
    OCR Engine using pytesseract for text recognition.
    """

    def __init__(self, lang: str = 'eng'):
        """
        Initializes the OCR engine with the specified language.
        Args:
            lang: Language code for OCR (default: 'eng').
        """
        self.lang = lang

    def recognize_text(self, img: Image.Image) -> Optional[str]:
        """
        Recognizes text from a PIL Image using pytesseract.
        Args:
            img: PIL.Image object.
        Returns:
            Recognized text as a string, or None if OCR fails.
        """
        try:
            text = pytesseract.image_to_string(img, lang=self.lang)
            return text.strip()
        except pytesseract.TesseractError as e:
            print(f"[ERROR] Tesseract OCR failed: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected OCR error: {e}")
            return None