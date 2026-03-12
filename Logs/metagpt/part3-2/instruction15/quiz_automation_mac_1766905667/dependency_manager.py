import sys
import subprocess
import platform
import shutil
from typing import Optional


class DependencyManager:
    """
    Handles installation and verification of Python, Homebrew, Tesseract, and pip dependencies on macOS.
    """

    MIN_PYTHON = (3, 9)
    TESSERACT_CMD = "tesseract"
    HOMEBREW_CMD = "/opt/homebrew/bin/brew" if platform.machine() == "arm64" else "/usr/local/bin/brew"
    REQUIREMENTS_FILE = "requirements.txt"

    @staticmethod
    def check_python_version() -> bool:
        """
        Checks if the current Python version meets the minimum requirement.
        Returns True if compatible, False otherwise.
        """
        if sys.version_info >= DependencyManager.MIN_PYTHON:
            print(f"[OK] Python version {sys.version_info.major}.{sys.version_info.minor} detected.")
            return True
        else:
            print(f"[ERROR] Python {DependencyManager.MIN_PYTHON[0]}.{DependencyManager.MIN_PYTHON[1]}+ required, "
                  f"but found {sys.version_info.major}.{sys.version_info.minor}.")
            return False

    @staticmethod
    def install_homebrew() -> bool:
        """
        Installs Homebrew if not already installed.
        Returns True if Homebrew is installed or was installed successfully, False otherwise.
        """
        brew_path = shutil.which("brew")
        if brew_path:
            print(f"[OK] Homebrew found at {brew_path}.")
            return True

        print("[INFO] Homebrew not found. Installing Homebrew...")
        try:
            # Official Homebrew install command
            subprocess.run(
                '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                shell=True, check=True)
            print("[OK] Homebrew installed successfully.")
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install Homebrew. Please install it manually from https://brew.sh/")
            return False

    @staticmethod
    def install_tesseract() -> bool:
        """
        Installs Tesseract OCR using Homebrew if not already installed.
        Returns True if Tesseract is installed or was installed successfully, False otherwise.
        """
        tesseract_path = shutil.which(DependencyManager.TESSERACT_CMD)
        if tesseract_path:
            print(f"[OK] Tesseract found at {tesseract_path}.")
            return True

        print("[INFO] Tesseract not found. Installing Tesseract via Homebrew...")
        brew_path = shutil.which("brew")
        if not brew_path:
            print("[ERROR] Homebrew is not installed. Cannot install Tesseract.")
            return False

        try:
            subprocess.run([brew_path, "install", "tesseract"], check=True)
            print("[OK] Tesseract installed successfully.")
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install Tesseract. Please install it manually: brew install tesseract")
            return False

    @staticmethod
    def install_pip_dependencies(requirements_file: Optional[str] = None) -> bool:
        """
        Installs pip dependencies from requirements.txt.
        Returns True if installation succeeded, False otherwise.
        """
        req_file = requirements_file or DependencyManager.REQUIREMENTS_FILE
        print(f"[INFO] Installing pip dependencies from {req_file}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)
            print("[OK] Pip dependencies installed successfully.")
            return True
        except subprocess.CalledProcessError:
            print(f"[ERROR] Failed to install pip dependencies from {req_file}.")
            return False

    @staticmethod
    def verify_installations() -> bool:
        """
        Verifies that all dependencies are installed and available.
        Returns True if all checks pass, False otherwise.
        """
        # Check Python version
        if not DependencyManager.check_python_version():
            return False

        # Check Homebrew
        if not DependencyManager.install_homebrew():
            return False

        # Check Tesseract
        if not DependencyManager.install_tesseract():
            return False

        # Check pip dependencies
        if not DependencyManager.install_pip_dependencies():
            return False

        # Check pytesseract import
        try:
            import pytesseract  # noqa: F401
            print("[OK] pytesseract is installed.")
        except ImportError:
            print("[ERROR] pytesseract is not installed.")
            return False

        # Check Pillow import
        try:
            from PIL import Image  # noqa: F401
            print("[OK] Pillow is installed.")
        except ImportError:
            print("[ERROR] Pillow is not installed.")
            return False

        # Check pynput import
        try:
            import pynput  # noqa: F401
            print("[OK] pynput is installed.")
        except ImportError:
            print("[ERROR] pynput is not installed.")
            return False

        print("[SUCCESS] All dependencies are installed and verified.")
        return True


if __name__ == "__main__":
    print("=== Dependency Check & Installation ===")
    if DependencyManager.verify_installations():
        print("All dependencies are ready.")
    else:
        print("Some dependencies failed to install or verify. Please check the messages above.")