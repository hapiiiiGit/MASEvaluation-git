import sys
import tkinter as tk
from ui import UI
from client_manager import ClientManager
from storage import Storage
from config import Config

class Main:
    """
    Entry point for the python_gpt4_test_automation_app.
    Initializes UI, ClientManager, and Storage, and starts the application.
    """

    def __init__(self):
        # Load configuration
        self.config = Config()
        # Initialize storage (SQLite or JSON)
        self.storage = Storage(self.config.get_storage_type(), self.config.get_storage_path())
        # Initialize client manager
        self.client_manager = ClientManager(self.storage)
        # Initialize UI
        self.root = tk.Tk()
        self.ui = UI(
            root=self.root,
            client_manager=self.client_manager,
            storage=self.storage,
            config=self.config
        )

    def run(self):
        """
        Starts the application UI.
        """
        self.ui.start()
        self.root.mainloop()

if __name__ == "__main__":
    app = Main()
    app.run()