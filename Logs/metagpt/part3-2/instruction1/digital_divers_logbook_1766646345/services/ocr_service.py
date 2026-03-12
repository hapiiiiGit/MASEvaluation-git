import os
from typing import Optional, Callable
from PIL import Image
import pytesseract

from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.core.window import Window

class OCRService:
    """
    OCRService provides methods to capture/select an image and extract text using pytesseract.
    It is designed for integration with Kivy UI for journal entry digitization.
    """

    def __init__(self, config):
        self.config = config
        # Optionally set tesseract_cmd if not in PATH
        tesseract_path = self.config.get('tesseract_cmd')
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def ocr_image(self, image_path: str) -> str:
        """
        Perform OCR on the given image file and return the extracted text.
        """
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            return f"OCR Error: {str(e)}"

    def open_ocr_dialog(self, target_textinput):
        """
        Opens a file chooser dialog for the user to select an image, performs OCR,
        and inserts the recognized text into the provided Kivy TextInput widget.
        """
        def on_file_selected(instance, selection):
            if selection and len(selection) > 0:
                image_path = selection[0]
                popup.dismiss()
                self._show_ocr_processing_popup(image_path, target_textinput)
            else:
                status_label.text = "No file selected."

        filechooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg', '*.bmp'])
        status_label = Label(text="Select an image for OCR", size_hint_y=None, height=30)
        select_btn = Button(text="Select", size_hint_y=None, height=40)
        cancel_btn = Button(text="Cancel", size_hint_y=None, height=40)

        def on_select_btn(instance):
            on_file_selected(instance, filechooser.selection)

        def on_cancel_btn(instance):
            popup.dismiss()

        select_btn.bind(on_release=on_select_btn)
        cancel_btn.bind(on_release=on_cancel_btn)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(status_label)
        layout.add_widget(filechooser)
        btn_layout = BoxLayout(size_hint_y=None, height=40)
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)

        popup = Popup(title="Select Image for OCR", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    def _show_ocr_processing_popup(self, image_path: str, target_textinput):
        """
        Shows a popup with OCR processing status and updates the target TextInput with the result.
        """
        status_label = Label(text="Processing OCR...", size_hint_y=None, height=30)
        img_widget = KivyImage(source=image_path, size_hint_y=None, height=200, allow_stretch=True)
        close_btn = Button(text="Close", size_hint_y=None, height=40)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(status_label)
        layout.add_widget(img_widget)
        layout.add_widget(close_btn)

        popup = Popup(title="OCR Processing", content=layout, size_hint=(0.7, 0.7))

        def do_ocr(*args):
            text = self.ocr_image(image_path)
            if target_textinput:
                target_textinput.text = (target_textinput.text or "") + "\n" + text
            status_label.text = "OCR Complete." if not text.startswith("OCR Error") else text

        close_btn.bind(on_release=popup.dismiss)
        popup.open()
        # Run OCR after popup is open to avoid UI freeze
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: do_ocr(), 0.5)