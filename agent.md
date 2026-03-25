# 🤖 Agent Instructions - NuraAgent (JARVIS)

This document defines the core principles, technical standards, and operational guidelines for AI agents working on the NuraAgent project.

---

## 🚀 1. The Core Mandate: Multi-Mode Feature Implementation

**IMPORTANT**: All new functionality must be implemented and exposed in both **CLI mode** and **API mode**. 

### Standard Workflow for Adding Features
1.  **Core Implementation (`/assistance/core/`)**: Place the logic and service classes here.
2.  **API Integration (`/assistance/apis/`)**: Add a corresponding FastAPI endpoint.
3.  **CLI Integration (`/assistance/cli/`)**: Add a menu option and the corresponding handler.

---

## 🛠️ 2. Technology Stack & Key Tools

-   **Backend Framework**: FastAPI (Asynchronous execution is mandatory for I/O).
-   **Validation**: Pydantic models for request/response payloads.
-   **AI Integration**: Ollama (`llama3:8b` by default) located at `http://localhost:11434`.
-   **Terminal UI**: Colorama for formatted console output.
-   **Logging**: Custom wrapper in `utils.logger` (always use `setup_logger("NAME")`).

---

## 📂 3. Project Architecture & Naming

-   **`/assistance/core/`**: The "brain" (Services like `ChatService`).
-   **`/assistance/apis/`**: The "web interface" (Controllers).
-   **`/assistance/cli/`**: The "user interface" (Terminal handlers and shell).
-   **`/assistance/utils/`**: Shared utilities (Logging, helper functions).
-   **`main.py`**: Uvicorn server launcher.
-   **`cli_run.py`**: CLI entry point.

**Branding**: The application name is **JARVIS**. Ensure error messages and user prompts reflect this identity.

---

## ✍️ 4. Technical Coding Standards

### ✅ Asynchronous Programming
-   Use `async/await` for any Ollama calls, file I/O, or network requests.
-   Use `httpx` or `aiohttp` for async HTTP calls.

### ✅ Error Handling & Status Codes
-   API endpoints should return appropriate **HTTP status codes** (200, 201, 400, 404, 500).
-   Use `HTTPException` from FastAPI to handle non-200 cases.
-   CLI handlers should provide helpful "next steps" or clear error descriptions to the user.

### ✅ Type Safety
-   Write type-hinted code for all functions (`def func(param: str) -> bool:`).
-   Use `Optional`, `List`, and `Union` types to improve clarity.

---

## 🏃 5. Verification & Testing

Before completing a task, verify the implementation:
1.  **API Verification**: Launch the server (`python assistance/main.py`) and test the `/docs` page or use a tool.
2.  **CLI Verification**: Launch the CLI (`python assistance/cli_run.py`) and ensure the new feature is accessible.
3.  **Logging**: Ensure relevant actions are logged at the correct level (`DEBUG`, `INFO`, `ERROR`).

