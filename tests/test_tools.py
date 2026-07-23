import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from tools import (
    create_todo_raw,
    delete_todo,
    list_todos,
    quick_add,
    update_todo,
)


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Use an in-memory SQLite database for testing tools."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    monkeypatch.setattr("database.engine", test_engine)
    monkeypatch.setattr("database.LocalSession", TestSession)
    yield


def test_create_todo_raw():
    res = create_todo_raw("Buy groceries", "Milk, Eggs", "high", "30-12-2026")
    assert "Task created successfully" in res

    tasks = list_todos.invoke({})
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Buy groceries"
    assert tasks[0]["priority"] == "high"
    assert tasks[0]["status"] == "pending"


def test_create_todo_empty_title():
    res = create_todo_raw("   ")
    assert "Error:" in res


def test_list_todos_filtering():
    create_todo_raw("Task 1", priority="high")
    create_todo_raw("Task 2", priority="low")

    # Update status of Task 1
    tasks = list_todos.invoke({})
    task1_id = tasks[0]["id"]
    update_todo.invoke({"todo_id": task1_id, "status": "done"})

    high_tasks = list_todos.invoke({"priority": "high"})
    assert len(high_tasks) == 1
    assert high_tasks[0]["title"] == "Task 1"

    done_tasks = list_todos.invoke({"status": "done"})
    assert len(done_tasks) == 1
    assert done_tasks[0]["title"] == "Task 1"


def test_update_todo():
    create_todo_raw("Initial Title", priority="low")
    tasks = list_todos.invoke({})
    todo_id = tasks[0]["id"]

    res = update_todo.invoke(
        {
            "todo_id": todo_id,
            "title": "Updated Title",
            "status": "in_progress",
            "priority": "high",
        }
    )
    assert "updated successfully" in res

    updated = list_todos.invoke({})[0]
    assert updated["title"] == "Updated Title"
    assert updated["status"] == "in_progress"
    assert updated["priority"] == "high"


def test_update_todo_invalid_id():
    res = update_todo.invoke({"todo_id": 999, "status": "done"})
    assert "Error: No task found" in res


def test_delete_todo():
    create_todo_raw("Task to Delete")
    tasks = list_todos.invoke({})
    todo_id = tasks[0]["id"]

    res = delete_todo.invoke({"todo_id": todo_id})
    assert "deleted successfully" in res

    remaining = list_todos.invoke({})
    assert len(remaining) == 0


def test_quick_add_parsing():
    res = quick_add.invoke({"user_text": "Finish project report tomorrow high priority"})
    assert "Task created successfully" in res

    tasks = list_todos.invoke({})
    assert len(tasks) == 1
    assert tasks[0]["priority"] == "high"
    assert "Finish project report" in tasks[0]["title"]
