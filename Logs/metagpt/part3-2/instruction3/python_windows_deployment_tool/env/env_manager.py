import os
import sys
import subprocess
import winreg

class EnvManager:
    """
    Configures system and user environment variables for Python and dependencies.
    Provides methods to set environment variables, update PATH, and ensure dependencies are accessible for all users.
    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.python_install_path = config.get("python_install_path", r"C:\Python{}".format(config.get("python_version", "3.11.8").replace('.', '')))
        self.env_vars = config.get("env_vars", {})
        self.dependency_paths = config.get("dependency_paths", [])
        self.update_path = config.get("update_path", True)

    def configure_environment(self):
        """
        Configures environment variables for both system and user scopes.
        """
        self.logger.info("Configuring environment variables...")
        # Set custom environment variables
        for var, value in self.env_vars.items():
            self.set_env_var_system(var, value)
            self.set_env_var_user(var, value)

        # Add Python and dependencies to PATH
        if self.update_path:
            self.add_to_path(self.python_install_path)
            for dep_path in self.dependency_paths:
                self.add_to_path(dep_path)

        self.logger.info("Environment variable configuration completed.")

    def set_env_var_system(self, var, value):
        """
        Sets a system-wide environment variable using Windows registry.
        """
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, var, 0, winreg.REG_EXPAND_SZ, value)
            self.logger.info(f"Set system environment variable: {var}={value}")
        except PermissionError:
            self.logger.error(f"Permission denied: Unable to set system environment variable {var}. Run as administrator.")
        except Exception as e:
            self.logger.error(f"Failed to set system environment variable {var}: {e}")

    def set_env_var_user(self, var, value):
        """
        Sets a user-specific environment variable using Windows registry.
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Environment",
                                0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, var, 0, winreg.REG_EXPAND_SZ, value)
            self.logger.info(f"Set user environment variable: {var}={value}")
        except Exception as e:
            self.logger.error(f"Failed to set user environment variable {var}: {e}")

    def add_to_path(self, new_path):
        """
        Adds a directory to both system and user PATH environment variables.
        """
        if not os.path.isdir(new_path):
            self.logger.warning(f"Path does not exist, skipping PATH update: {new_path}")
            return

        # Update system PATH
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                0, winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
                path_value, _ = winreg.QueryValueEx(key, "Path")
                paths = path_value.split(";")
                if new_path not in paths:
                    paths.append(new_path)
                    new_path_value = ";".join(paths)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path_value)
                    self.logger.info(f"Added {new_path} to system PATH")
        except PermissionError:
            self.logger.error(f"Permission denied: Unable to update system PATH. Run as administrator.")
        except Exception as e:
            self.logger.error(f"Failed to update system PATH: {e}")

        # Update user PATH
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Environment",
                                0, winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
                try:
                    path_value, _ = winreg.QueryValueEx(key, "Path")
                except FileNotFoundError:
                    path_value = ""
                paths = path_value.split(";") if path_value else []
                if new_path not in paths:
                    paths.append(new_path)
                    new_path_value = ";".join(paths)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path_value)
                    self.logger.info(f"Added {new_path} to user PATH")
        except Exception as e:
            self.logger.error(f"Failed to update user PATH: {e}")

        # Update current process PATH for immediate effect
        os.environ["PATH"] = os.environ.get("PATH", "") + ";" + new_path

    def refresh_environment(self):
        """
        Notifies the system that environment variables have changed.
        """
        try:
            # Broadcast WM_SETTINGCHANGE to all windows
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            result = ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 0x0002, 5000, None
            )
            self.logger.info("Broadcasted environment change to system.")
        except Exception as e:
            self.logger.warning(f"Failed to broadcast environment change: {e}")