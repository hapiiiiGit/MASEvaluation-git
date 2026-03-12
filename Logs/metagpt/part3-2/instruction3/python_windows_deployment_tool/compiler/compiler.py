import os
import sys
import subprocess
import shutil

class Compiler:
    """
    Compiles Python scripts into standalone .exe files using PyInstaller or cx_Freeze.
    Provides methods to select the packaging tool, run the compilation process, and return the path to the generated executable.
    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.last_exe_path = None

    def compile(self, script_path, packager="pyinstaller"):
        """
        Compiles the given Python script into a standalone .exe file using the specified packager.
        Returns the path to the generated executable, or None on failure.
        """
        if not os.path.isfile(script_path):
            self.logger.error(f"Script not found: {script_path}")
            return None

        output_dir = self.config.get("build_output_dir", "dist")
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        if packager.lower() == "pyinstaller":
            exe_path = self._compile_with_pyinstaller(script_path, output_dir)
        elif packager.lower() == "cx_freeze":
            exe_path = self._compile_with_cx_freeze(script_path, output_dir)
        else:
            self.logger.error(f"Unknown packager: {packager}")
            return None

        if exe_path and os.path.isfile(exe_path):
            self.last_exe_path = exe_path
            self.logger.info(f"Executable created: {exe_path}")
            return exe_path
        else:
            self.logger.error("Failed to create executable.")
            return None

    def get_last_exe_path(self):
        """
        Returns the path to the last successfully built executable.
        """
        return self.last_exe_path

    def _compile_with_pyinstaller(self, script_path, output_dir):
        """
        Uses PyInstaller to compile the script.
        """
        self.logger.info("Compiling with PyInstaller...")
        exe_name = self._get_exe_name(script_path)
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--distpath", output_dir,
            "--name", exe_name,
            script_path
        ]
        try:
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.logger.info(result.stdout.decode())
            exe_path = os.path.join(output_dir, exe_name + ".exe")
            if os.path.isfile(exe_path):
                return exe_path
            else:
                # Try to find the exe in the output directory
                for f in os.listdir(output_dir):
                    if f.lower().endswith(".exe"):
                        return os.path.join(output_dir, f)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"PyInstaller failed: {e.stderr.decode() if e.stderr else e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during PyInstaller compilation: {e}")
        return None

    def _compile_with_cx_freeze(self, script_path, output_dir):
        """
        Uses cx_Freeze to compile the script.
        """
        self.logger.info("Compiling with cx_Freeze...")
        exe_name = self._get_exe_name(script_path)
        build_dir = os.path.join(output_dir, "build_cxfreeze")
        if not os.path.isdir(build_dir):
            os.makedirs(build_dir, exist_ok=True)
        # Create a setup.py for cx_Freeze
        setup_code = f"""
import sys
from cx_Freeze import setup, Executable

setup(
    name="{exe_name}",
    version="1.0",
    description="Standalone executable built with cx_Freeze",
    executables=[Executable("{script_path}", base=None)]
)
"""
        setup_path = os.path.join(build_dir, "setup_cxfreeze.py")
        with open(setup_path, "w", encoding="utf-8") as f:
            f.write(setup_code)
        try:
            cmd = [
                sys.executable, setup_path, "build", "--build-exe", build_dir
            ]
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=build_dir)
            self.logger.info(result.stdout.decode())
            # Find the exe in the build directory
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    if file.lower().endswith(".exe"):
                        exe_path = os.path.join(root, file)
                        # Copy to output_dir for consistency
                        final_exe_path = os.path.join(output_dir, exe_name + ".exe")
                        shutil.copy2(exe_path, final_exe_path)
                        return final_exe_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"cx_Freeze failed: {e.stderr.decode() if e.stderr else e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during cx_Freeze compilation: {e}")
        return None

    def _get_exe_name(self, script_path):
        """
        Returns the base name for the executable, without extension.
        """
        base = os.path.basename(script_path)
        name, _ = os.path.splitext(base)
        return name