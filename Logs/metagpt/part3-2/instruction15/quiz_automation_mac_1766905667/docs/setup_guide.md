# Quiz Automation for macOS – Setup & Usage Guide

Welcome to **quiz_automation_mac**! This guide will help you install, configure, and use the Python-based quiz automation script for macOS. The tool captures your screen, recognizes quiz text using OCR, and is triggered by a hotkey. It supports Retina displays and is easy to set up.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Script](#running-the-script)
5. [Hotkey Usage](#hotkey-usage)
6. [Retina Display & Region Selection](#retina-display--region-selection)
7. [Troubleshooting](#troubleshooting)
8. [Credits](#credits)

---

## Prerequisites

- **macOS** (Intel or Apple Silicon)
- **Python 3.9+** ([Download Python](https://www.python.org/downloads/))
- **Homebrew** (will be installed automatically if missing)
- **Tesseract OCR** (will be installed automatically if missing)
- **Internet connection** (for dependency installation)

---

## Installation

1. **Download or Clone the Repository**

   ```
   git clone <your-repo-url>
   cd quiz_automation_mac_1766905667
   ```

2. **Run the Setup Script**

   The setup script will:
   - Check for Python 3.9+
   - Install Homebrew (if missing)
   - Install Tesseract OCR (if missing)
   - Upgrade pip
   - Install all required Python packages

   ```
   chmod +x setup.sh
   ./setup.sh
   ```

   If you encounter permission issues, try:
   ```
   sudo ./setup.sh
   ```

---

## Configuration

Configuration is managed via `config.json` in the project root. The script will create this file with defaults if it does not exist.

**Default config:**