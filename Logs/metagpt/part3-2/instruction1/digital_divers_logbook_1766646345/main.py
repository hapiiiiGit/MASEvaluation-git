import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window

# Import services (implementations are in their respective files)
from services.auth_service import AuthService
from services.cloud_service import CloudService
from services.ocr_service import OCRService
from services.export_service import ExportService
from services.validation_service import ValidationService

# Utils
from utils.config import Config
from utils.encryption import Encryption

# Models
from models.user import User
from models.logbook import Logbook

# Set window size for desktop testing
Window.size = (400, 700)

# Load .kv files
KV_PATH = os.path.join(os.path.dirname(__file__), "ui")
Builder.load_file(os.path.join(KV_PATH, "dashboard.kv"))
Builder.load_file(os.path.join(KV_PATH, "log_entry.kv"))
Builder.load_file(os.path.join(KV_PATH, "export.kv"))
Builder.load_file(os.path.join(KV_PATH, "login.kv"))

# Screen definitions
class LoginScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class LogEntryScreen(Screen):
    pass

class ExportScreen(Screen):
    pass

class DigitalDiversLogbookApp(App):
    def build(self):
        # Initialize services
        self.config = Config()
        self.encryption = Encryption(self.config)
        self.auth_service = AuthService(self.config, self.encryption)
        self.cloud_service = CloudService(self.config)
        self.ocr_service = OCRService(self.config)
        self.export_service = ExportService(self.config)
        self.validation_service = ValidationService(self.config)

        # Models
        self.user = None
        self.logbook = Logbook(self.config)

        # Screen manager setup
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(LogEntryScreen(name='log_entry'))
        self.sm.add_widget(ExportScreen(name='export'))

        # Start at login screen
        return self.sm

    def on_start(self):
        # Attempt auto-login if credentials are stored
        if self.auth_service.is_authenticated():
            self.user = self.auth_service.get_current_user()
            self.sm.current = 'dashboard'
        else:
            self.sm.current = 'login'

    def login_success(self, user: User):
        self.user = user
        self.sm.current = 'dashboard'

    def logout(self):
        self.auth_service.logout()
        self.user = None
        self.sm.current = 'login'

    def open_log_entry(self, entry_id=None):
        log_entry_screen = self.sm.get_screen('log_entry')
        log_entry_screen.entry_id = entry_id
        log_entry_screen.load_entry(entry_id)
        self.sm.current = 'log_entry'

    def open_export(self):
        self.sm.current = 'export'

    def open_dashboard(self):
        self.sm.current = 'dashboard'

    # Expose services for screens to use
    def get_services(self):
        return {
            "auth": self.auth_service,
            "cloud": self.cloud_service,
            "ocr": self.ocr_service,
            "export": self.export_service,
            "validation": self.validation_service,
            "encryption": self.encryption,
            "config": self.config,
            "logbook": self.logbook,
            "user": self.user,
        }

if __name__ == '__main__':
    DigitalDiversLogbookApp().run()