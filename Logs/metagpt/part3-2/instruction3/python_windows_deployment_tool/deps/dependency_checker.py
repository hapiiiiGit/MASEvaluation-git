import os
import subprocess
import sys

class DependencyChecker:
    """
    Verifies and installs required Python packages from requirements.txt.
    Provides methods to check for missing dependencies and install them using pip.
    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.requirements_path = config.get("requirements_path", "requirements.txt")
        self.python_executable = self._get_python_executable()

    def _get_python_executable(self):
        # Prefer configured Python install path, else use system python
        python_install_path = self.config.get("python_install_path")
        python_version = self.config.get("python_version")
        if python_install_path and python_version:
            python_exe = os.path.join(python_install_path, "python.exe")
            if os.path.isfile(python_exe):
                return python_exe
        return sys.executable

    def verify_and_install(self):
        """
        Verifies and installs all required Python packages.
        Returns True if all dependencies are satisfied, False otherwise.
        """
        if not os.path.isfile(self.requirements_path):
            self.logger.error(f"requirements.txt not found at {self.requirements_path}")
            return False

        self.logger.info(f"Checking and installing dependencies from {self.requirements_path}")

        # Check for missing packages using pip
        try:
            # pip install -r requirements.txt
            cmd = [
                self.python_executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip"
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.logger.info("Upgraded pip to latest version.")

            cmd = [
                self.python_executable,
                "-m",
                "pip",
                "install",
                "-r",
                self.requirements_path
            ]
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.logger.info(result.stdout.decode())
            self.logger.info("All dependencies are installed and up to date.")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Dependency installation failed: {e.stderr.decode() if e.stderr else e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during dependency installation: {e}")
            return False