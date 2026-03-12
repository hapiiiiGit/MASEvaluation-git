import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from excel_manager import ExcelManager
from error_categorizer import ErrorCategorizer
from rag_knowledge_base import RAGKnowledgeBase
from gpt4_api import GPT4API

class UI:
    """
    Tkinter-based user interface for python_gpt4_test_automation_app.
    Provides dashboard, file upload/download, error report viewing, and client selection.
    """

    def __init__(self, root, client_manager, storage, config):
        self.root = root
        self.client_manager = client_manager
        self.storage = storage
        self.config = config

        self.gpt4_api = GPT4API(self.config.get_gpt4_api_key())
        self.excel_manager = ExcelManager()
        self.error_categorizer = ErrorCategorizer()
        self.rag_kb = RAGKnowledgeBase(self.storage)

        self.current_client_id = None
        self.input_data = None
        self.output_data = None
        self.error_list = None

        self.root.title("GPT-4 Test Automation App")
        self.root.geometry("900x600")
        self._build_login_screen()

    def start(self):
        self.root.deiconify()

    def _build_login_screen(self):
        self._clear_root()
        self.login_frame = ttk.Frame(self.root, padding=30)
        self.login_frame.pack(expand=True)

        ttk.Label(self.login_frame, text="Login", font=("Arial", 18)).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self.login_frame, text="Username:").grid(row=1, column=0, sticky="e", pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=1, column=1, pady=5)
        ttk.Label(self.login_frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        self.login_btn = ttk.Button(self.login_frame, text="Login", command=self._login)
        self.login_btn.grid(row=3, column=0, columnspan=2, pady=15)

    def _login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        client_id = self.client_manager.authenticate(username, password)
        if client_id:
            self.current_client_id = client_id
            self._build_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def _build_dashboard(self):
        self._clear_root()
        self.dashboard_frame = ttk.Frame(self.root, padding=10)
        self.dashboard_frame.pack(fill="both", expand=True)

        # Client selector
        ttk.Label(self.dashboard_frame, text="Select Client:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        self.client_selector = ttk.Combobox(self.dashboard_frame, values=self.client_manager.get_clients(), state="readonly")
        self.client_selector.set(self.current_client_id)
        self.client_selector.grid(row=0, column=1, sticky="w")
        self.client_selector.bind("<<ComboboxSelected>>", self._on_client_selected)

        # File upload/download
        ttk.Label(self.dashboard_frame, text="Input Excel File:").grid(row=1, column=0, sticky="w", pady=5)
        self.upload_input_btn = ttk.Button(self.dashboard_frame, text="Upload", command=self.upload_file)
        self.upload_input_btn.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(self.dashboard_frame, text="Output Excel File:").grid(row=2, column=0, sticky="w", pady=5)
        self.upload_output_btn = ttk.Button(self.dashboard_frame, text="Upload", command=self.upload_output_file)
        self.upload_output_btn.grid(row=2, column=1, sticky="w", pady=5)

        self.download_btn = ttk.Button(self.dashboard_frame, text="Download Last Input", command=self.download_file)
        self.download_btn.grid(row=3, column=1, sticky="w", pady=5)

        # Generate new test input
        self.generate_btn = ttk.Button(self.dashboard_frame, text="Generate New Test Input", command=self.generate_test_input)
        self.generate_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Error report
        self.error_report_btn = ttk.Button(self.dashboard_frame, text="View Error Report", command=self.show_error_report)
        self.error_report_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Knowledge base access
        ttk.Label(self.dashboard_frame, text="Knowledge Base Query:").grid(row=6, column=0, sticky="w", pady=5)
        self.kb_query_entry = ttk.Entry(self.dashboard_frame, width=40)
        self.kb_query_entry.grid(row=6, column=1, sticky="w", pady=5)
        self.kb_search_btn = ttk.Button(self.dashboard_frame, text="Search KB", command=self.search_knowledge_base)
        self.kb_search_btn.grid(row=7, column=1, sticky="w", pady=5)

        # Improved input suggestion
        self.improve_input_btn = ttk.Button(self.dashboard_frame, text="Suggest Improved Input", command=self.suggest_improved_input)
        self.improve_input_btn.grid(row=8, column=0, columnspan=2, pady=10)

        # Status
        self.status_label = ttk.Label(self.dashboard_frame, text="", foreground="blue")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=10)

        # Error report table
        self.error_report_tree = None

    def _on_client_selected(self, event):
        self.current_client_id = self.client_selector.get()
        self.status_label.config(text=f"Switched to client: {self.current_client_id}")

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Input Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file_path:
            try:
                self.input_data = self.excel_manager.analyze_output_excel(file_path)
                self.storage.save_data(self.current_client_id, {"input_data": self.input_data})
                self.status_label.config(text=f"Input file uploaded and analyzed for client {self.current_client_id}.")
            except Exception as e:
                messagebox.showerror("Upload Error", f"Failed to upload input file: {str(e)}")

    def upload_output_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Output Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file_path:
            try:
                self.output_data = self.excel_manager.analyze_output_excel(file_path)
                self.storage.save_data(self.current_client_id, {"output_data": self.output_data})
                self.status_label.config(text=f"Output file uploaded and analyzed for client {self.current_client_id}.")
            except Exception as e:
                messagebox.showerror("Upload Error", f"Failed to upload output file: {str(e)}")

    def download_file(self):
        data = self.storage.load_data(self.current_client_id)
        if data and "input_data" in data:
            save_path = filedialog.asksaveasfilename(
                title="Save Input Excel File",
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx *.xls")]
            )
            if save_path:
                try:
                    self.excel_manager.create_input_excel(data["input_data"], save_path)
                    self.status_label.config(text=f"Input file downloaded for client {self.current_client_id}.")
                except Exception as e:
                    messagebox.showerror("Download Error", f"Failed to download input file: {str(e)}")
        else:
            messagebox.showinfo("No Data", "No input data available for download.")

    def generate_test_input(self):
        prompt = "Generate test input for automated test scenarios."
        try:
            test_input = self.gpt4_api.generate_test_input(prompt)
            save_path = filedialog.asksaveasfilename(
                title="Save Generated Input Excel File",
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx *.xls")]
            )
            if save_path:
                self.excel_manager.create_input_excel(test_input, save_path)
                self.storage.save_data(self.current_client_id, {"input_data": test_input})
                self.status_label.config(text=f"Test input generated and saved for client {self.current_client_id}.")
        except Exception as e:
            messagebox.showerror("Generation Error", f"Failed to generate test input: {str(e)}")

    def show_error_report(self):
        data = self.storage.load_data(self.current_client_id)
        if data and "output_data" in data:
            try:
                self.error_list = self.error_categorizer.categorize_errors(data["output_data"])
                self.rag_kb.log_test_data(self.current_client_id, data.get("input_data", {}), data["output_data"], self.error_list)
                self._show_error_report_table(self.error_list)
                self.status_label.config(text=f"Error report generated for client {self.current_client_id}.")
            except Exception as e:
                messagebox.showerror("Error Report", f"Failed to generate error report: {str(e)}")
        else:
            messagebox.showinfo("No Data", "No output data available for error report.")

    def _show_error_report_table(self, error_list):
        if self.error_report_tree:
            self.error_report_tree.destroy()
        self.error_report_tree = ttk.Treeview(self.dashboard_frame, columns=("Category", "Description"), show="headings", height=10)
        self.error_report_tree.heading("Category", text="Category")
        self.error_report_tree.heading("Description", text="Description")
        self.error_report_tree.grid(row=10, column=0, columnspan=2, pady=10, sticky="nsew")
        for error in error_list:
            self.error_report_tree.insert("", "end", values=(error.get("category", ""), error.get("description", "")))

    def search_knowledge_base(self):
        query = self.kb_query_entry.get()
        if not query:
            messagebox.showinfo("No Query", "Please enter a query to search the knowledge base.")
            return
        try:
            results = self.rag_kb.retrieve_similar_cases(query, self.current_client_id)
            result_str = "\n".join([str(r) for r in results]) if results else "No similar cases found."
            messagebox.showinfo("Knowledge Base Results", result_str)
        except Exception as e:
            messagebox.showerror("Knowledge Base Error", f"Failed to search knowledge base: {str(e)}")

    def suggest_improved_input(self):
        try:
            improved_input = self.rag_kb.improve_input_generation(self.current_client_id)
            messagebox.showinfo("Improved Input Suggestion", str(improved_input))
        except Exception as e:
            messagebox.showerror("Improvement Error", f"Failed to suggest improved input: {str(e)}")

    def _clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()