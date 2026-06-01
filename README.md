# AI Task Manager

AI Task Manager is a Streamlit app for creating and managing tasks with natural language. It combines a chat assistant, quick-add flow, and a card-based dashboard backed by SQLite.

## Live App

Open the deployed app here:

https://aadityabhuree-ai-task-manager-app-khqoxk.streamlit.app

## What It Does

- Create tasks from plain English input
- Detect priority keywords like `high`, `medium`, and `low`
- Parse simple due-date phrases such as `today`, `tomorrow`, and `in 3 days`
- List, update, and delete tasks through the assistant chat
- Show tasks in a cleaner dashboard layout with status and priority chips

## Stack

- Python
- Streamlit
- LangChain
- LangGraph
- Google Gemini (`gemini-2.5-flash`)
- SQLite

## Getting Started

### 1. Install dependencies

Use the project requirements file:

```bash
pip install -r requirements.txt
```

### 2. Add environment variables

Create a `.env.local` file in the project root and add your Google API key:

```bash
GOOGLE_API_KEY=your_api_key_here
```

### 3. Run the app

Launch Streamlit:

```bash
streamlit run app.py
```

## Using the App

### Quick Add

Type a task in natural language, for example:

- `Buy milk tomorrow high priority`
- `Prepare slides in 2 days`
- `Call dentist this week medium priority`

### Assistant Chat

Use the chat panel to ask things like:

- `List all my tasks`
- `Mark task 3 as done`
- `Show pending tasks`
- `Delete task 5`

## Project Structure

- `app.py` - Streamlit interface and dashboard layout
- `agent.py` - LangChain agent setup and memory
- `tools.py` - Task CRUD tools and quick-add parser
- `database.py` - SQLite models and session helpers
- `README.md` - Project overview and usage guide

## Data and Storage

- Tasks are stored locally in `todo.db`
- Chat state uses `InMemorySaver`, which is best suited for development and testing
- The app initializes the database automatically on startup

## Notes

- If the Gemini API key is missing, the assistant will not work correctly.
- `requirements.txt` is the main dependency file used by the project.
- There is also a `requirement.txt` file in the repo, but `requirements.txt` is the one referenced by the app documentation.