# AI Task Manager

AI Task Manager is a Streamlit app that helps you create, track, and manage tasks with natural language. It uses LangChain, Google Gemini, and SQLite to provide a chat-based task assistant plus a quick-add dashboard.

## Features

- Quick add tasks from plain English
- Auto-detect priority and due dates when possible
- Chat with the task assistant to create, list, update, or delete tasks
- Visual task dashboard with status and priority cards
- SQLite-backed storage for local persistence

## Tech Stack

- Python
- Streamlit
- LangChain
- LangGraph
- Google Gemini (`gemini-2.5-flash`)
- SQLite

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your Google API key to `.env.local`:

```bash
GOOGLE_API_KEY=your_api_key_here
```

## Run the App

Start the Streamlit app with:

```bash
streamlit run app.py
```

## Project Files

- `app.py` - Streamlit UI
- `agent.py` - LangChain agent setup
- `tools.py` - Task CRUD tools
- `database.py` - SQLite models and session setup

## Notes

- The app stores data in `todo.db`.
- The agent uses in-memory checkpointing for chat state.
- `InMemorySaver` is intended for testing and development.