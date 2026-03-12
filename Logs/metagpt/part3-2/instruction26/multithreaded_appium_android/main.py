import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import Config
from device_manager import DeviceManager
from session_manager import SessionManager
from test_runner import TestRunner
from monitor import Monitor
from logger import Logger

def main():
    # Initialize logger
    logger = Logger()
    logger.log("Starting multithreaded Appium automation system.", "INFO")

    # Load configuration
    try:
        config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
        config = Config.load(config_path)
        logger.log(f"Loaded configuration from {config_path}", "INFO")
    except Exception as e:
        logger.log_error(e)
        sys.exit(1)

    # Discover devices
    device_manager = DeviceManager(config.devices)
    try:
        device_manager.discover_devices()
        available_devices = device_manager.get_available_devices()
        logger.log(f"Discovered {len(available_devices)} available devices.", "INFO")
    except Exception as e:
        logger.log_error(e)
        sys.exit(1)

    if not available_devices:
        logger.log("No available devices found. Exiting.", "ERROR")
        sys.exit(1)

    # Initialize session manager
    session_manager = SessionManager()
    sessions = []
    session_threads = []
    session_lock = threading.Lock()

    # Start Appium sessions for each device (up to max_concurrent_sessions)
    max_sessions = min(config.max_concurrent_sessions, len(available_devices))
    logger.log(f"Starting up to {max_sessions} Appium sessions.", "INFO")

    def start_session_thread(device):
        try:
            session = session_manager.start_session(device)
            with session_lock:
                sessions.append(session)
            logger.log(f"Started session {session.session_id} for device {device.device_id}", "INFO")
        except Exception as e:
            logger.log_error(e)
            session_manager.handle_failure(device.device_id, e)

    threads = []
    for device in available_devices[:max_sessions]:
        t = threading.Thread(target=start_session_thread, args=(device,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    if not sessions:
        logger.log("No sessions started successfully. Exiting.", "ERROR")
        sys.exit(1)

    # Initialize test runner
    test_runner = TestRunner()
    test_scripts = config.test_scripts

    # Run tests in parallel using ThreadPoolExecutor
    logger.log("Running tests on all sessions.", "INFO")
    test_results = {}
    with ThreadPoolExecutor(max_workers=max_sessions) as executor:
        future_to_session = {
            executor.submit(test_runner.run_tests, [session], test_scripts): session.session_id
            for session in sessions
        }
        for future in as_completed(future_to_session):
            session_id = future_to_session[future]
            try:
                result_dict = future.result()
                test_results.update(result_dict)
                logger.log(f"Test completed for session {session_id}.", "INFO")
            except Exception as e:
                logger.log_error(e)
                session_manager.handle_failure(session_id, e)

    # Monitor system metrics and report status
    monitor = Monitor(sessions)
    try:
        metrics = monitor.collect_metrics()
        monitor.report_status()
        logger.log(f"System metrics: {metrics}", "INFO")
    except Exception as e:
        logger.log_error(e)

    # Stop all sessions
    logger.log("Stopping all sessions.", "INFO")
    for session in sessions:
        try:
            session_manager.stop_session(session.session_id)
            logger.log(f"Stopped session {session.session_id}.", "INFO")
        except Exception as e:
            logger.log_error(e)

    # Print summary of test results
    logger.log("Test Results Summary:", "INFO")
    for session_id, result in test_results.items():
        logger.log(
            f"Session {session_id}: Success={result.success}, Details={result.details}, Timestamp={result.timestamp}",
            "INFO"
        )

    logger.log("Multithreaded Appium automation system finished.", "INFO")

if __name__ == "__main__":
    main()