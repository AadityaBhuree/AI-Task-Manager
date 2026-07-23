# AI Task Manager

[![CI/CD Pipeline](https://github.com/AadityaBhuree/AI-Task-Manager/actions/workflows/ci.yml/badge.svg)](https://github.com/AadityaBhuree/AI-Task-Manager/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

AI Task Manager is an interactive Streamlit application for creating and managing tasks with natural language processing. It combines an AI agent, quick-add parsing, status/priority filtering, and direct card-level task actions backed by SQLite.

---

## 🚀 Features

- **Natural Language Parsing**: Create tasks from plain English text (e.g. `Buy milk tomorrow high priority`).
- **Automatic Priority & Date Extraction**: Detects `low`, `medium`, `high` priority keywords and parses relative dates (`today`, `tomorrow`, `next Monday`).
- **Interactive Task Dashboard**: Filter tasks by status (`Pending`, `In Progress`, `Done`), search by keyword, and perform one-click actions (**Mark Done**, **Delete**).
- **AI Assistant Chat**: Natural language chat assistant powered by LangChain and Google Gemini.
- **Robust Code Hygiene**: Formatted with `ruff`, typed with `mypy`, and tested with `pytest`.
- **Automated CI/CD Pipeline**: Continuous integration with GitHub Actions running linters, type checks, test suite with coverage, and container builds.

---

## 🛠️ Stack

- **Frontend & UI**: Streamlit
- **AI Engine & Framework**: LangChain, LangGraph, Google Gemini (`gemini-1.5-flash`)
- **Database & ORM**: SQLite, SQLAlchemy
- **DevOps & QA**: Pytest, Pytest-Cov, Ruff, Mypy, Docker, GitHub Actions CI/CD

---

## 💻 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/AadityaBhuree/AI-Task-Manager.git
cd AI-Task-Manager
```

### 2. Set up environment variables
Copy the template and set your `GOOGLE_API_KEY`:
```bash
cp .env.example .env.local
```

### 3. Install dependencies
```bash
pip install -r requirements-dev.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

---

## 🧪 Testing & Code Quality

Run the test suite and linters locally:

```bash
# Run pytest test suite with coverage
pytest --cov=.

# Run code formatter check
ruff format --check .

# Run linter
ruff check .

# Run type checker
mypy database.py tools.py agent.py
```

---

## 🐳 Docker Deployment

Build and run using Docker:

```bash
docker build -t ai-task-manager .
docker run -p 8501:8501 --env-file .env.local ai-task-manager
```

---

## 📁 Repository Structure

```text
AI-Task-Manager/
├── .github/workflows/    # GitHub Actions CI/CD pipeline
├── tests/                # Automated pytest unit test suite
│   ├── test_database.py
│   ├── test_tools.py
│   └── test_agent.py
├── app.py                # Main Streamlit dashboard UI
├── agent.py              # LangChain AI agent & processing logic
├── tools.py              # CRUD tools & natural language quick-add parser
├── database.py           # SQLAlchemy database models & session scope
├── pyproject.toml        # Ruff, Mypy, and Pytest configuration
├── Dockerfile            # Container build specification
├── requirements.txt      # Production Python dependencies
└── requirements-dev.txt  # Developer & CI tooling dependencies
```