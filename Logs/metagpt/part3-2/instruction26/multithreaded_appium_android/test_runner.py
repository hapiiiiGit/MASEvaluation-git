import importlib.util
import os
import traceback
from typing import List, Dict

from session_manager import AppiumSession
from logger import Logger
from datetime import datetime

class TestResult:
    def __init__(self, session_id: str, success: bool, details: str, timestamp: datetime):
        self.session_id = session_id
        self.success = success
        self.details = details
        self.timestamp = timestamp

    def __repr__(self):
        return (f"TestResult(session_id={self.session_id}, success={self.success}, "
                f"details={self.details}, timestamp={self.timestamp})")

class TestRunner:
    """
    Executes UI interaction scripts on each AppiumSession and collects results.
    """
    def __init__(self):
        self.logger = Logger()

    def run_tests(self, sessions: List[AppiumSession], test_scripts: List[str]) -> Dict[str, TestResult]:
        """
        Run the provided test scripts on each AppiumSession.
        Returns a dictionary mapping session_id to TestResult.
        """
        results = {}
        for session in sessions:
            session_result = self._run_session_tests(session, test_scripts)
            results[session.session_id] = session_result
        return results

    def _run_session_tests(self, session: AppiumSession, test_scripts: List[str]) -> TestResult:
        """
        Run all test scripts on a single AppiumSession.
        Each test script should be a Python file with a 'run_test(driver)' function.
        """
        success = True
        details = ""
        for script_path in test_scripts:
            try:
                if not os.path.isfile(script_path):
                    raise FileNotFoundError(f"Test script not found: {script_path}")

                # Dynamically import the test script as a module
                module_name = os.path.splitext(os.path.basename(script_path))[0]
                spec = importlib.util.spec_from_file_location(module_name, script_path)
                test_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(test_module)

                # Run the test function
                if not hasattr(test_module, "run_test"):
                    raise AttributeError(f"Test script {script_path} does not have a 'run_test(driver)' function.")

                self.logger.log(f"Running test '{script_path}' on session {session.session_id}", "INFO")
                test_module.run_test(session.driver)
                details += f"Test '{script_path}': PASSED\n"
            except Exception as e:
                success = False
                error_msg = f"Test '{script_path}': FAILED - {str(e)}\n{traceback.format_exc()}\n"
                details += error_msg
                self.logger.log_error(e)
        timestamp = datetime.now()
        return TestResult(session.session_id, success, details, timestamp)