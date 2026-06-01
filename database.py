
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///todo.db" ###PGsQL

engine = create_engine(DATABASE_URL)
LocalSession = sessionmaker(bind=engine)

Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(String(500), default="")
    status = Column(String(20), default="pending") #pending, in_progress, done
    priority = Column(String(20), default="medium") #0: low, 1: medium, 2: high
    due_date = Column(String(20), default="")
    created_at = Column(String(20), default="")

    def to_dict(self)-> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
            "created_at": self.created_at
        }
        
def init_db():
    Base.metadata.create_all(bind=engine)