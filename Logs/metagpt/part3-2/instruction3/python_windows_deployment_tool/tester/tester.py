import os
import subprocess
import tempfile
import getpass
import shutil

class Tester:
    """
    Automates testing of generated executables across multiple user accounts.
    Provides methods to run the .exe under different user contexts, collect output, and report results.
    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.test_users = config.get("test_users", [])  # List of dicts: [{"username": "...", "password": "..."}]
        self.test_args = config.get("test_args", [])    # Optional arguments to pass to the executable
        self.test_timeout = config.get("test_timeout", 30)  # Timeout in seconds for each test run

    def test_executable_multiuser(self, exe_path):
        """
        Tests the given executable across multiple user accounts.
        Returns a dict with overall success and per-user results.
        """
        if not os.path.isfile(exe_path):
            self.logger.error(f"Executable not found: {exe_path}")
            return {"success": False, "results": []}

        if not self.test_users:
            self.logger.warning("No test users specified in configuration. Running test as current user only.")
            return self._test_as_current_user(exe_path)

        results = []
        all_success = True

        for user in self.test_users:
            username = user.get("username")
            password = user.get("password")
            if not username or not password:
                self.logger.error(f"Missing username or password for test user: {user}")
                results.append({
                    "username": username,
                    "success": False,
                    "error": "Missing credentials"
                })
                all_success = False
                continue

            self.logger.info(f"Testing executable as user: {username}")
            result = self._run_as_user(exe_path, username, password)
            results.append(result)
            if not result["success"]:
                all_success = False

        return {"success": all_success, "results": results}

    def _test_as_current_user(self, exe_path):
        """
        Runs the executable as the current user.
        """
        username = getpass.getuser()
        self.logger.info(f"Testing executable as current user: {username}")
        try:
            cmd = [exe_path] + self.test_args
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.test_timeout,
                check=False
            )
            output = proc.stdout.decode(errors="ignore")
            error = proc.stderr.decode(errors="ignore")
            success = proc.returncode == 0
            if success:
                self.logger.info(f"Test succeeded for user {username}. Output:\n{output}")
            else:
                self.logger.error(f"Test failed for user {username}. Error:\n{error}")
            return {
                "success": success,
                "results": [{
                    "username": username,
                    "output": output,
                    "error": error,
                    "returncode": proc.returncode
                }]
            }
        except Exception as e:
            self.logger.error(f"Exception during test as current user: {e}")
            return {
                "success": False,
                "results": [{
                    "username": username,
                    "output": "",
                    "error": str(e),
                    "returncode": -1
                }]
            }

    def _run_as_user(self, exe_path, username, password):
        """
        Runs the executable as a different user using 'runas' and a temporary batch file.
        Returns a dict with the result.
        """
        # Create a temporary batch file to run the executable and redirect output
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.txt")
            error_file = os.path.join(tmpdir, "error.txt")
            batch_file = os.path.join(tmpdir, "run_test.bat")

            exe_cmd = f'"{exe_path}" {" ".join(self.test_args)} > "{output_file}" 2> "{error_file}"'
            with open(batch_file, "w", encoding="utf-8") as f:
                f.write(f'@echo off\n{exe_cmd}\n')

            # Use 'runas' to execute the batch file as the target user
            # Note: Windows 'runas' does not accept password via command line for security reasons.
            # To automate, we use 'psexec' if available, else prompt for password.
            psexec_path = shutil.which("psexec")
            if psexec_path:
                run_cmd = [
                    psexec_path,
                    "-accepteula",
                    "-u", username,
                    "-p", password,
                    "-d",  # Don't wait for process to finish (we'll poll for output)
                    "cmd.exe", "/c", batch_file
                ]
                try:
                    proc = subprocess.run(
                        run_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=self.test_timeout,
                        check=False
                    )
                    # Wait for output files to be created
                    waited = 0
                    while not os.path.exists(output_file) and waited < self.test_timeout:
                        import time
                        time.sleep(1)
                        waited += 1
                    output = ""
                    error = ""
                    if os.path.exists(output_file):
                        with open(output_file, "r", encoding="utf-8", errors="ignore") as f:
                            output = f.read()
                    if os.path.exists(error_file):
                        with open(error_file, "r", encoding="utf-8", errors="ignore") as f:
                            error = f.read()
                    success = proc.returncode == 0 and not error
                    if success:
                        self.logger.info(f"Test succeeded for user {username}. Output:\n{output}")
                    else:
                        self.logger.error(f"Test failed for user {username}. Error:\n{error}")
                    return {
                        "username": username,
                        "success": success,
                        "output": output,
                        "error": error,
                        "returncode": proc.returncode
                    }
                except Exception as e:
                    self.logger.error(f"Exception during test as user {username}: {e}")
                    return {
                        "username": username,
                        "success": False,
                        "output": "",
                        "error": str(e),
                        "returncode": -1
                    }
            else:
                # Fallback: runas (interactive, cannot automate password)
                self.logger.warning("PsExec not found. 'runas' will prompt for password interactively.")
                run_cmd = [
                    "runas",
                    f"/user:{username}",
                    f'cmd.exe /c "{batch_file}"'
                ]
                try:
                    proc = subprocess.run(
                        run_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=self.test_timeout,
                        check=False
                    )
                    output = ""
                    error = ""
                    if os.path.exists(output_file):
                        with open(output_file, "r", encoding="utf-8", errors="ignore") as f:
                            output = f.read()
                    if os.path.exists(error_file):
                        with open(error_file, "r", encoding="utf-8", errors="ignore") as f:
                            error = f.read()
                    success = proc.returncode == 0 and not error
                    if success:
                        self.logger.info(f"Test succeeded for user {username}. Output:\n{output}")
                    else:
                        self.logger.error(f"Test failed for user {username}. Error:\n{error}")
                    return {
                        "username": username,
                        "success": success,
                        "output": output,
                        "error": error,
                        "returncode": proc.returncode
                    }
                except Exception as e:
                    self.logger.error(f"Exception during test as user {username}: {e}")
                    return {
                        "username": username,
                        "success": False,
                        "output": "",
                        "error": str(e),
                        "returncode": -1
                    }