# Codebase Intelligence & Memory

> **Project:** AI Task Manager
> **Role:** Codebase Intelligence Agent

---

## 📌 REPOSITORY DISCOVERY

### Root Structure
- `app.py`: Main Streamlit UI, status filters, card actions, and chat interface.
- `agent.py`: LangChain agent setup, memory checkpointer, and query coercion helpers.
- `tools.py`: CRUD tools (`create_todo`, `list_todos`, `update_todo`, `delete_todo`, `quick_add`).
- `database.py`: SQLAlchemy models (`Todo`) and session context manager (`get_db_session`).
- `tests/`: Automated unit test suite (`test_database.py`, `test_tools.py`, `test_agent.py`).
- `.github/workflows/ci.yml`: GitHub Actions CI/CD workflow.
- `pyproject.toml`: Tool configurations for `ruff`, `mypy`, and `pytest`.
- `requirements.txt`: Production Python dependencies.
- `requirements-dev.txt`: Development, linting, and testing dependencies.

---

## 🛠️ TECHNOLOGY DETECTION

### Frontend / UI Framework
- **Framework:** Streamlit (Python)

### Backend & AI Framework
- **Core:** Python 3.10+
- **LLM Engine:** Google Gemini (`gemini-1.5-flash`)
- **AI Orchestration:** LangChain & LangGraph (Stateful Agent with `InMemorySaver`)

### Database
- **Engine:** SQLite (`todo.db`)
- **ORM:** SQLAlchemy (with session context management and auto-rollback)

---

## 🏗️ ARCHITECTURE & DATA FLOW

```text
[ User (Web Browser) ]
       │
       ▼
[ Streamlit UI (app.py) ]
       │
       ├─► [ Direct Actions / Quick Add ] ──► [ Tools (tools.py) ]
       │                                            │
       ├─► [ Agent Chat (agent.py) ] ──────────────┤
       │         │                                  │
       │         ▼                                  ▼
       │   [ Gemini API ]                   [ Database Layer (database.py) ]
       │                                            │
       ▼                                            ▼
[ Interactive Dashboard UI ] ◄────────────── [ SQLite Database (todo.db) ]
```
