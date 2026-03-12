import os
import sys
import threading

from dependency_manager import DependencyManager
from screenshot_util import ScreenshotUtil
from ocr_engine import OCREngine
from hotkey_listener import HotkeyListener
from config import Config

CONFIG_PATH = "config.json"

def display_ocr_result(text: str):
    """
    Display the OCR result to the user.
    For CLI, print to console. For GUI, could use a popup (not implemented).
    """
    print("\n=== OCR Result ===")
    print(text if text else "[No text recognized]")
    print("==================\n")

def on_hotkey_triggered():
    """
    Callback for hotkey press: capture screenshot, handle Retina scaling, run OCR, display result.
    """
    try:
        region = config.get("region", None)
        print("[INFO] Capturing screenshot...")
        img = ScreenshotUtil.capture_screen(region)
        img = ScreenshotUtil.handle_retina_scaling(img)
        print("[INFO] Running OCR...")
        text = ocr_engine.recognize_text(img)
        display_ocr_result(text)
    except Exception as e:
        print(f"[ERROR] Exception during hotkey automation: {e}")

def main():
    print("=== Quiz Automation for macOS ===")

    # Step 1: Dependency check and installation
    print("[STEP] Verifying dependencies...")
    if not DependencyManager.verify_installations():
        print("[FATAL] Dependency verification failed. Exiting.")
        sys.exit(1)

    # Step 2: Load configuration
    print("[STEP] Loading configuration...")
    global config
    config = Config.load_config(CONFIG_PATH)
    hotkey = Config.get_hotkey(config)
    ocr_lang = Config.get_ocr_lang(config)
    region = Config.get_region(config)

    # Step 3: Initialize OCR engine
    global ocr_engine
    ocr_engine = OCREngine(lang=ocr_lang)

    # Step 4: Set up hotkey listener
    print(f"[STEP] Setting up hotkey listener for: {hotkey}")
    listener = HotkeyListener(hotkey, on_hotkey_triggered)
    listener.start_listening()

    print("[INFO] Press the configured hotkey to capture a screenshot and run OCR.")
    print("[INFO] Press Ctrl+C to exit.")

    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n[INFO] Exiting quiz automation.")
        listener.stop_listening()
        sys.exit(0)

if __name__ == "__main__":
    # Use globals for callback access
    config = None
    ocr_engine = None
    main()