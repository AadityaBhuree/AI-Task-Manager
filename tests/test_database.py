import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, Todo, get_db_session


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Use an in-memory SQLite database for testing."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    monkeypatch.setattr("database.engine", test_engine)
    monkeypatch.setattr("database.LocalSession", TestSession)
    yield


def test_todo_creation_and_to_dict():
    with get_db_session() as session:
        todo = Todo(
            title="Test Task",
            description="Testing DB model",
            priority="high",
            status="pending",
            due_date="01-01-2026",
            created_at="23-07-2026 12:00:00",
        )
        session.add(todo)
        session.flush()
        todo_id = todo.id

    with get_db_session() as session:
        fetched = session.query(Todo).filter(Todo.id == todo_id).first()
        assert fetched is not None
        assert fetched.title == "Test Task"
        assert fetched.priority == "high"

        data = fetched.to_dict()
        assert data["id"] == todo_id
        assert data["title"] == "Test Task"
        assert data["description"] == "Testing DB model"
        assert data["priority"] == "high"
        assert data["status"] == "pending"


def test_db_session_rollback_on_error():
    with pytest.raises(ValueError, match="Simulated Error"):
        with get_db_session() as session:
            todo = Todo(title="Rollback Task")
            session.add(todo)
            raise ValueError("Simulated Error")

    with get_db_session() as session:
        count = session.query(Todo).filter(Todo.title == "Rollback Task").count()
        assert count == 0
