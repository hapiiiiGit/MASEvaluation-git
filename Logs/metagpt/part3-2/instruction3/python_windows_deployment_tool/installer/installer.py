import os
import sys
import platform
import subprocess
import shutil
import requests

class PythonInstaller:
    """
    Handles Python installation on Windows.
    Detects system architecture and Python version, downloads the correct installer if needed, and performs installation.
    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.python_version = config.get("python_version", "3.11.8")
        self.install_path = config.get("python_install_path", r"C:\Python{}".format(self.python_version.replace('.', '')))
        self.architecture = self._detect_architecture()
        self.installer_url = self._get_installer_url()
        self.installer_filename = os.path.join(os.getenv("TEMP", "."), f"python-{self.python_version}-{self.architecture}.exe")

    def _detect_architecture(self):
        arch = platform.architecture()[0]
        if arch == "64bit":
            return "amd64"
        else:
            return "win32"

    def _get_installer_url(self):
        # Official Python download URLs
        base_url = f"https://www.python.org/ftp/python/{self.python_version}/"
        if self.architecture == "amd64":
            filename = f"python-{self.python_version}-amd64.exe"
        else:
            filename = f"python-{self.python_version}.exe"
        return base_url + filename

    def is_python_installed(self):
        """
        Checks if the required Python version is installed.
        """
        try:
            # Try to find python executable in install_path
            python_exe = os.path.join(self.install_path, "python.exe")
            if os.path.isfile(python_exe):
                output = subprocess.check_output([python_exe, "--version"], stderr=subprocess.STDOUT)
                version_str = output.decode().strip().split()[-1]
                if version_str == self.python_version:
                    self.logger.info(f"Python {self.python_version} found at {python_exe}")
                    return True
            # Try system python
            output = subprocess.check_output(["python", "--version"], stderr=subprocess.STDOUT)
            version_str = output.decode().strip().split()[-1]
            if version_str == self.python_version:
                self.logger.info(f"Python {self.python_version} found in system PATH")
                return True
        except Exception as e:
            self.logger.warning(f"Python version check failed: {e}")
        return False

    def install_python(self):
        """
        Downloads and installs Python if not already installed.
        """
        self.logger.info(f"Preparing to install Python {self.python_version} ({self.architecture})")
        # Download installer
        if not os.path.isfile(self.installer_filename):
            self.logger.info(f"Downloading Python installer from {self.installer_url}")
            try:
                with requests.get(self.installer_url, stream=True, timeout=60) as r:
                    r.raise_for_status()
                    with open(self.installer_filename, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                self.logger.info(f"Downloaded installer to {self.installer_filename}")
            except Exception as e:
                self.logger.error(f"Failed to download Python installer: {e}")
                return False
        else:
            self.logger.info(f"Installer already downloaded: {self.installer_filename}")

        # Run installer silently
        install_args = [
            self.installer_filename,
            "/quiet",
            "InstallAllUsers=1",
            f"TargetDir={self.install_path}",
            "PrependPath=1",
            "Include_pip=1"
        ]
        self.logger.info(f"Running installer: {' '.join(install_args)}")
        try:
            result = subprocess.run(install_args, check=True)
            self.logger.info("Python installation completed.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Python installer failed: {e}")
            return False

        # Verify installation
        python_exe = os.path.join(self.install_path, "python.exe")
        if os.path.isfile(python_exe):
            self.logger.info(f"Python installed at {python_exe}")
            return True
        else:
            self.logger.error(f"Python executable not found after installation: {python_exe}")
            return False