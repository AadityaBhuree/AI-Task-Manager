from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from dateparser.search import search_dates
from langchain.tools import tool

from database import Todo, get_db_session

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"pending", "in_progress", "done"}


def create_todo_raw(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: str = "",
) -> str:
    """Core logic to create and save a new todo task."""
    if not title or not title.strip():
        return "Error: Task title cannot be empty."

    task_priority = priority.lower().strip() if priority else "medium"
    if task_priority not in VALID_PRIORITIES:
        task_priority = "medium"

    created_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    with get_db_session() as session:
        todo = Todo(
            title=title.strip()[:200],
            description=(description or "").strip()[:500],
            priority=task_priority,
            due_date=(due_date or "").strip(),
            created_at=created_time,
            status="pending",
        )
        session.add(todo)
        session.flush()
        task_id = todo.id

    return f"Task created successfully with ID: {task_id}"


@tool
def create_todo(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: str = "",
) -> str:
    """Create and save a new todo task.

    Args:
        title: Short title of the task (required).
        description: Optional detailed note of the task.
        priority: 'low', 'medium', or 'high' (default is 'medium').
        due_date: Due date e.g. '25-05-2026' (optional).
    """
    return create_todo_raw(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
    )


@tool
def list_todos(
    status: str | None = None,
    priority: str | None = None,
) -> list[dict[str, Any]]:
    """List all todo tasks, with optional filtering by status and priority.

    Args:
        status: Filter tasks by status ('pending', 'in_progress', 'done').
        priority: Filter tasks by priority ('low', 'medium', 'high').
    """
    with get_db_session() as session:
        query = session.query(Todo)

        if status and status != "all":
            query = query.filter(Todo.status == status.lower().strip())

        if priority and priority != "all":
            query = query.filter(Todo.priority == priority.lower().strip())

        todos = query.order_by(Todo.id.asc()).all()
        return [todo.to_dict() for todo in todos]


@tool
def quick_add(user_text: str) -> str:
    """Quick add a todo using natural language.

    Example: "Buy milk tomorrow morning high priority"
    Extracts priority and due date automatically.
    """
    if not user_text or not user_text.strip():
        return "Error: No text provided for quick add."

    text = user_text.strip()
    text_lower = text.lower()

    # Detect priority
    detected_priority = "medium"
    for p in ["high", "medium", "low"]:
        if re.search(rf"\b{p}\b", text_lower):
            detected_priority = p
            text = re.sub(rf"\b{p}\b", "", text, flags=re.IGNORECASE)
            break

    # Detect date phrase
    due_date = ""
    try:
        dates = search_dates(text, settings={"PREFER_DATES_FROM": "future"})
    except Exception:
        dates = None

    if dates:
        matched_text, dt = dates[0]
        due_date = dt.strftime("%d-%m-%Y")
        text = text.replace(matched_text, "")

    # Clean action verbs/phrases
    text = re.sub(
        r"(?i)\b(remind me to|add|create|please|task:|todo:)\b",
        "",
        text,
    )
    cleaned_title = re.sub(r"\s+", " ", text).strip()
    if not cleaned_title:
        cleaned_title = "New Task"

    return create_todo_raw(
        title=cleaned_title,
        description="",
        priority=detected_priority,
        due_date=due_date,
    )


@tool
def update_todo(
    todo_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    due_date: str | None = None,
) -> str:
    """Update an existing todo task by its ID.

    Args:
        todo_id: The unique identifier of the task to update (required).
        title: New title for the task (optional).
        description: New description for the task (optional).
        status: New status ('pending', 'in_progress', 'done') (optional).
        priority: New priority ('low', 'medium', 'high') (optional).
        due_date: New due date e.g. '25-05-2026' (optional).
    """
    with get_db_session() as session:
        todo = session.query(Todo).filter(Todo.id == todo_id).first()

        if not todo:
            return f"Error: No task found with ID: {todo_id}"

        if title is not None and title.strip():
            todo.title = title.strip()[:200]
        if description is not None:
            todo.description = description.strip()[:500]
        if status is not None:
            norm_status = status.lower().strip()
            if norm_status in VALID_STATUSES:
                todo.status = norm_status
        if priority is not None:
            norm_priority = priority.lower().strip()
            if norm_priority in VALID_PRIORITIES:
                todo.priority = norm_priority
        if due_date is not None:
            todo.due_date = due_date.strip()

        return f"Task with ID: {todo_id} updated successfully."


@tool
def delete_todo(todo_id: int) -> str:
    """Delete a todo task by its ID.

    Args:
        todo_id: The unique identifier of the task to delete (required).
    """
    with get_db_session() as session:
        todo = session.query(Todo).filter(Todo.id == todo_id).first()

        if not todo:
            return f"Error: No task found with ID: {todo_id}"

        session.delete(todo)
        return f"Task with ID: {todo_id} deleted successfully."