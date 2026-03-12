import argparse
import sys
import os
import yaml

from utils.logger import get_logger
from installer.installer import PythonInstaller
from env.env_manager import EnvManager
from deps.dependency_checker import DependencyChecker
from compiler.compiler import Compiler
from tester.tester import Tester

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "config.yaml")

def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(
        description="Python Windows Deployment Tool: Automate Python installation, environment setup, dependency management, compilation, and testing."
    )
    parser.add_argument(
        "--config",
        type=str,
        default=CONFIG_PATH,
        help="Path to configuration YAML file."
    )
    parser.add_argument(
        "--step",
        type=str,
        choices=["all", "install", "env", "deps", "compile", "test"],
        default="all",
        help="Run a specific step or the entire workflow."
    )
    parser.add_argument(
        "--script",
        type=str,
        default=None,
        help="Path to the main Python script to compile."
    )
    parser.add_argument(
        "--packager",
        type=str,
        choices=["pyinstaller", "cx_freeze"],
        default=None,
        help="Packaging tool to use for compilation."
    )
    args = parser.parse_args()

    config = load_config(args.config)
    logger = get_logger(config.get("log_file", "deployment.log"), config.get("log_level", "INFO"))

    logger.info("Starting Python Windows Deployment Tool")

    # Step 1: Install Python
    if args.step in ("all", "install"):
        logger.info("Step 1: Python installation")
        installer = PythonInstaller(config, logger)
        if not installer.is_python_installed():
            success = installer.install_python()
            if not success:
                logger.error("Python installation failed. Exiting.")
                sys.exit(1)
        else:
            logger.info("Required Python version already installed.")

    # Step 2: Configure environment variables
    if args.step in ("all", "env"):
        logger.info("Step 2: Environment variable configuration")
        env_manager = EnvManager(config, logger)
        env_manager.configure_environment()

    # Step 3: Dependency verification and installation
    if args.step in ("all", "deps"):
        logger.info("Step 3: Dependency verification and installation")
        dep_checker = DependencyChecker(config, logger)
        if not dep_checker.verify_and_install():
            logger.error("Dependency verification/installation failed. Exiting.")
            sys.exit(1)

    # Step 4: Compilation to .exe
    if args.step in ("all", "compile"):
        logger.info("Step 4: Compilation to .exe")
        compiler = Compiler(config, logger)
        script_path = args.script or config.get("main_script")
        if not script_path or not os.path.isfile(script_path):
            logger.error(f"Main script not specified or does not exist: {script_path}")
            sys.exit(1)
        packager = args.packager or config.get("packager", "pyinstaller")
        exe_path = compiler.compile(script_path, packager)
        if not exe_path or not os.path.isfile(exe_path):
            logger.error("Compilation failed. Exiting.")
            sys.exit(1)
        logger.info(f"Executable created at: {exe_path}")

    # Step 5: Multi-user testing
    if args.step in ("all", "test"):
        logger.info("Step 5: Multi-user executable testing")
        tester = Tester(config, logger)
        exe_path = compiler.get_last_exe_path() if args.step == "all" else None
        if not exe_path:
            exe_path = config.get("last_exe_path") or input("Path to executable for testing: ").strip()
        if not exe_path or not os.path.isfile(exe_path):
            logger.error(f"Executable not found for testing: {exe_path}")
            sys.exit(1)
        test_results = tester.test_executable_multiuser(exe_path)
        if not test_results["success"]:
            logger.error("Testing failed for one or more user accounts.")
            sys.exit(1)
        logger.info("Testing completed successfully for all user accounts.")

    logger.info("Deployment workflow completed successfully.")

if __name__ == "__main__":
    main()