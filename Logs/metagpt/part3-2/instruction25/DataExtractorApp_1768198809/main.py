import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QTabWidget, QFormLayout, QProgressBar, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Import extraction modules (to be implemented in subsequent tasks)
import web_extractor
import pdf_extractor
import data_manager

class WebExtractionThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object, object)  # (data, error)

    def __init__(self, url, username, password):
        super().__init__()
        self.url = url
        self.username = username
        self.password = password

    def run(self):
        try:
            self.progress.emit(10)
            data = web_extractor.extract_data(self.url, self.username, self.password)
            self.progress.emit(100)
            self.finished.emit(data, None)
        except Exception as e:
            self.finished.emit(None, str(e))

class PDFExtractionThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object, object)  # (data, error)

    def __init__(self, pdf_paths):
        super().__init__()
        self.pdf_paths = pdf_paths

    def run(self):
        try:
            self.progress.emit(10)
            data = pdf_extractor.extract_data(self.pdf_paths)
            self.progress.emit(100)
            self.finished.emit(data, None)
        except Exception as e:
            self.finished.emit(None, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Extractor App")
        self.setMinimumSize(700, 500)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.web_tab = QWidget()
        self.pdf_tab = QWidget()
        self.output_tab = QWidget()

        self.tabs.addTab(self.web_tab, "Web Extraction")
        self.tabs.addTab(self.pdf_tab, "PDF Extraction")
        self.tabs.addTab(self.output_tab, "Output & Save")

        self._init_web_tab()
        self._init_pdf_tab()
        self._init_output_tab()

        self.web_data = None
        self.pdf_data = None
        self.extracted_pdfs = []

    def _init_web_tab(self):
        layout = QFormLayout()
        self.web_url_input = QLineEdit()
        self.web_username_input = QLineEdit()
        self.web_password_input = QLineEdit()
        self.web_password_input.setEchoMode(QLineEdit.Password)
        self.web_extract_btn = QPushButton("Extract Data from Web")
        self.web_progress = QProgressBar()
        self.web_progress.setValue(0)

        layout.addRow(QLabel("Web Page URL:"), self.web_url_input)
        layout.addRow(QLabel("Username:"), self.web_username_input)
        layout.addRow(QLabel("Password:"), self.web_password_input)
        layout.addRow(self.web_extract_btn)
        layout.addRow(self.web_progress)

        self.web_tab.setLayout(layout)
        self.web_extract_btn.clicked.connect(self._start_web_extraction)

    def _init_pdf_tab(self):
        layout = QVBoxLayout()
        self.pdf_list = QListWidget()
        self.pdf_add_btn = QPushButton("Add PDF Files")
        self.pdf_remove_btn = QPushButton("Remove Selected")
        self.pdf_extract_btn = QPushButton("Extract Data from PDFs")
        self.pdf_progress = QProgressBar()
        self.pdf_progress.setValue(0)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.pdf_add_btn)
        btn_layout.addWidget(self.pdf_remove_btn)

        layout.addWidget(QLabel("PDF Files:"))
        layout.addWidget(self.pdf_list)
        layout.addLayout(btn_layout)
        layout.addWidget(self.pdf_extract_btn)
        layout.addWidget(self.pdf_progress)

        self.pdf_tab.setLayout(layout)
        self.pdf_add_btn.clicked.connect(self._add_pdf_files)
        self.pdf_remove_btn.clicked.connect(self._remove_selected_pdfs)
        self.pdf_extract_btn.clicked.connect(self._start_pdf_extraction)

    def _init_output_tab(self):
        layout = QFormLayout()
        self.output_folder_input = QLineEdit()
        self.output_folder_btn = QPushButton("Select Output Folder")
        self.save_excel_btn = QPushButton("Save Data to Excel")
        self.save_excel_btn.setEnabled(False)
        self.output_status = QLabel("")

        layout.addRow(QLabel("Output Folder:"), self.output_folder_input)
        layout.addRow(self.output_folder_btn)
        layout.addRow(self.save_excel_btn)
        layout.addRow(self.output_status)

        self.output_tab.setLayout(layout)
        self.output_folder_btn.clicked.connect(self._select_output_folder)
        self.save_excel_btn.clicked.connect(self._save_to_excel)

    def _start_web_extraction(self):
        url = self.web_url_input.text().strip()
        username = self.web_username_input.text().strip()
        password = self.web_password_input.text().strip()
        if not url or not username or not password:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return
        self.web_extract_btn.setEnabled(False)
        self.web_progress.setValue(0)
        self.web_thread = WebExtractionThread(url, username, password)
        self.web_thread.progress.connect(self.web_progress.setValue)
        self.web_thread.finished.connect(self._web_extraction_finished)
        self.web_thread.start()

    def _web_extraction_finished(self, data, error):
        self.web_extract_btn.setEnabled(True)
        if error:
            QMessageBox.critical(self, "Web Extraction Error", error)
            self.web_data = None
        else:
            QMessageBox.information(self, "Success", "Web data extracted successfully.")
            self.web_data = data
        self._update_save_button_state()

    def _add_pdf_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        for f in files:
            if f not in [self.pdf_list.item(i).text() for i in range(self.pdf_list.count())]:
                self.pdf_list.addItem(QListWidgetItem(f))

    def _remove_selected_pdfs(self):
        for item in self.pdf_list.selectedItems():
            self.pdf_list.takeItem(self.pdf_list.row(item))

    def _start_pdf_extraction(self):
        pdf_paths = [self.pdf_list.item(i).text() for i in range(self.pdf_list.count())]
        if not pdf_paths:
            QMessageBox.warning(self, "Input Error", "Please add at least one PDF file.")
            return
        self.pdf_extract_btn.setEnabled(False)
        self.pdf_progress.setValue(0)
        self.pdf_thread = PDFExtractionThread(pdf_paths)
        self.pdf_thread.progress.connect(self.pdf_progress.setValue)
        self.pdf_thread.finished.connect(self._pdf_extraction_finished)
        self.pdf_thread.start()

    def _pdf_extraction_finished(self, data, error):
        self.pdf_extract_btn.setEnabled(True)
        if error:
            QMessageBox.critical(self, "PDF Extraction Error", error)
            self.pdf_data = None
        else:
            QMessageBox.information(self, "Success", "PDF data extracted successfully.")
            self.pdf_data = data
            self.extracted_pdfs = [self.pdf_list.item(i).text() for i in range(self.pdf_list.count())]
        self._update_save_button_state()

    def _select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder_input.setText(folder)
        self._update_save_button_state()

    def _update_save_button_state(self):
        if (self.web_data or self.pdf_data) and self.output_folder_input.text().strip():
            self.save_excel_btn.setEnabled(True)
        else:
            self.save_excel_btn.setEnabled(False)

    def _save_to_excel(self):
        output_folder = self.output_folder_input.text().strip()
        if not output_folder:
            QMessageBox.warning(self, "Output Error", "Please select an output folder.")
            return

        try:
            # Save structured data to Excel and organize PDFs
            excel_path, pdf_folder = data_manager.save_data(
                web_data=self.web_data,
                pdf_data=self.pdf_data,
                pdf_files=self.extracted_pdfs,
                output_folder=output_folder
            )
            self.output_status.setText(
                f"Data saved to Excel: {excel_path}\nPDFs stored in: {pdf_folder}"
            )
            QMessageBox.information(self, "Success", "Data and PDFs saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))
            self.output_status.setText(f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()