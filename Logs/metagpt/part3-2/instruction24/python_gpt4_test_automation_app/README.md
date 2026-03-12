# python_gpt4_test_automation_app

## Overview

**python_gpt4_test_automation_app** is a Python standalone desktop application (packaged as a .exe) designed to automate the generation and analysis of test scenario Excel files using the GPT-4 API. It supports error categorization, logs all data into a Retrieval-Augmented Generation (RAG) knowledge base, and continuously improves input generation based on historical data. The application is built for multi-client environments with secure, isolated local storage using either SQLite or JSON.

---

## Features

- **GPT-4 API Integration:** Generate test input Excel files for automated test scenarios.
- **Excel File Management:** Create and analyze input/output Excel files.
- **Error Categorization:** Modular, configurable error categorization logic.
- **RAG Knowledge Base:** Log all test data and errors for retrieval and improvement.
- **Continuous Improvement:** Suggest improved test inputs based on historical errors.
- **Multi-Client Support:** Data isolation and secure access for multiple clients.
- **Local Storage:** Configurable backend (SQLite or JSON).
- **Simple UI:** Tkinter-based dashboard for file management, error reports, and client selection.

---

## Architecture

- **main.py:** Entry point, initializes UI, ClientManager, and Storage.
- **ui.py:** Tkinter-based user interface.
- **gpt4_api.py:** GPT-4 API integration.
- **excel_manager.py:** Excel file creation and analysis (openpyxl, pandas).
- **error_categorizer.py:** Error categorization logic.
- **rag_knowledge_base.py:** RAG knowledge base operations.
- **client_manager.py:** User authentication and client management.
- **storage.py:** Local storage backend (SQLite/JSON).
- **config.py:** Configuration management.
- **requirements.txt:** Python dependencies.

See `docs/system_design.md` for detailed architecture, class diagrams, and sequence diagrams.

---

## Setup & Installation

### Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)
- GPT-4 API key from OpenAI

### Install Dependencies
