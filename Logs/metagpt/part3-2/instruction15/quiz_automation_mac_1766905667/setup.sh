#!/bin/bash

# setup.sh - Automated setup for quiz_automation_mac on macOS
# Installs Homebrew, Tesseract, Python 3, and all Python dependencies from requirements.txt

set -e

echo "=== Quiz Automation for macOS: Setup Script ==="

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Check Python version (3.9+)
PYTHON_BIN=$(which python3 || true)
if [ -z "$PYTHON_BIN" ]; then
    echo "[ERROR] Python3 not found. Please install Python 3.9 or newer from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MINOR" -lt 9 ]; then
    echo "[ERROR] Python 3.9+ is required. Found Python $PYTHON_VERSION."
    exit 1
fi
echo "[OK] Python $PYTHON_VERSION detected."

# 2. Install Homebrew if missing
if ! command_exists brew; then
    echo "[INFO] Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo "[OK] Homebrew installed."
else
    echo "[OK] Homebrew is already installed."
fi

# 3. Install Tesseract if missing
if ! command_exists tesseract; then
    echo "[INFO] Tesseract not found. Installing Tesseract via Homebrew..."
    brew install tesseract
    echo "[OK] Tesseract installed."
else
    echo "[OK] Tesseract is already installed."
fi

# 4. Upgrade pip
echo "[INFO] Upgrading pip..."
$PYTHON_BIN -m pip install --upgrade pip

# 5. Install Python dependencies
REQ_FILE="requirements.txt"
if [ ! -f "$REQ_FILE" ]; then
    echo "[ERROR] requirements.txt not found in current directory."
    exit 1
fi

echo "[INFO] Installing Python dependencies from $REQ_FILE..."
$PYTHON_BIN -m pip install -r "$REQ_FILE"
echo "[OK] Python dependencies installed."

# 6. Verify installation
echo "[INFO] Verifying installation..."
$PYTHON_BIN -c "import pytesseract, PIL, pynput, numpy; print('[OK] All Python dependencies are installed.')"

echo "=== Setup Complete! ==="
echo "You can now run: python3 main.py"