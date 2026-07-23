from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "sqlite:///todo.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


class Todo(Base):
    """SQLAlchemy model for storing todo tasks."""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(String(500), default="")
    status = Column(String(20), default="pending")  # 'pending', 'in_progress', 'done'
    priority = Column(String(20), default="medium")  # 'low', 'medium', 'high'
    due_date = Column(String(20), default="")
    created_at = Column(String(20), default="")

    def to_dict(self) -> dict[str, Any]:
        """Serialize model attributes into a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "status": self.status or "pending",
            "priority": self.priority or "medium",
            "due_date": self.due_date or "",
            "created_at": self.created_at or "",
        }


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = LocalSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(db_engine=engine) -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=db_engine)