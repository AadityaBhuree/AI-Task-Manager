from langchain.tools import tool
from database import LocalSession , Todo
from datetime import datetime
from dateparser.search import search_dates
import re


#CRUD

@tool
def create_todo(title: str, description: str = "", priority: str ="medium",due_date: str = ""):
    """
    Create and save a new todo task.
    
    Args:
        title :Short title of the task (required).
        description: Optional detailed note of the task.
        priority : 'low', 'medium', or 'high' (default is 'medium').
        due_date : Due date eg. '25-05-2026 (optional).
    """

    return create_todo_raw(title=title, description=description, priority=priority, due_date=due_date)


def create_todo_raw(title: str, description: str = "", priority: str ="medium", due_date: str = ""):
    task_priorities = "medium"
    if priority and priority.lower() in ["low", "medium", "high"]:
        task_priorities = priority.lower()

    with LocalSession() as session:
        todo = Todo(
            title=title.strip()[:200],
            description=(description or "")[:500],
            priority=task_priorities,
            due_date=due_date,
            created_at=datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        )
        session.add(todo)
        session.commit()

        session.refresh(todo)
        return f"Task created successfully with ID: {todo.id}"
    

@tool
def list_todos(status: str = None, priority: str = None):
    """
    List all todo tasks, with optional filtering by status and priority.
    
    Args:
        status : Filter tasks by their status ('pending', 'in_progress', 'done').
        priority : Filter tasks by their priority ('low', 'medium', 'high').
    """
    with LocalSession() as session:
        query = session.query(Todo)

        if status and status != "all":
            query = query.filter(Todo.status == status)

        if priority and priority != "all":
            query = query.filter(Todo.priority == priority)
        
        todos = query.order_by(Todo.id).all()
        
        if not todos:
            return "No tasks found for your filter values."

        allTodos = {todo.id: todo for todo in todos}
        return allTodos


@tool
def quick_add(user_text: str):
    """
    Quick add a todo using natural language. Example: "Buy milk tomorrow morning high priority"
    This will attempt to extract a due date and priority and create the task.
    """
    if not user_text or not user_text.strip():
        return "No text provided for quick add."

    text = user_text.strip()
    text_lower = text.lower()

    # detect priority
    priority = None
    for p in ["high", "medium", "low"]:
        if re.search(rf"\b{p}\b", text_lower):
            priority = p
            # remove priority word from title
            text = re.sub(rf"\b{p}\b", "", text, flags=re.IGNORECASE)
            break

    # find date expressions
    due_date = ""
    try:
        dates = search_dates(text, settings={"PREFER_DATES_FROM": "future"})
    except Exception:
        dates = None

    if dates:
        # take first detected date
        matched_text, dt = dates[0]
        due_date = dt.strftime("%d-%m-%Y")
        # remove matched date phrase from title
        text = text.replace(matched_text, "")

    # clean common verbs/phrases
    text = re.sub(r"(?i)remind me to |(?i)add |(?i)create |(?i)please |(?i)task:|(?i)todo:", "", text)
    title = re.sub(r"\s+", " ", text).strip()
    if not title:
        title = "New Task"

    return create_todo_raw(title=title, description="", priority=(priority or "medium"), due_date=due_date)


@tool
def update_todo(
    todo_id: int,
    title: str = None,
    description: str = None,
    status: str = None,
    priority: str = None,
    due_date: str = None):
    """
    Update an existing todo task by its ID.
    
    Args:
        todo_id : The unique identifier of the task to update (required).
        title : New title for the task (optional).
        description: New description for the task (optional).
        status : New status ('pending', 'in_progress', 'done') (optional).
        priority : New priority ('low', 'medium', 'high') (optional).
        due_date : New due date eg. '25-05-2026' (optional).
    """
    with LocalSession() as session:
        todo = session.query(Todo).filter(Todo.id == todo_id).first()
        
        if not todo:
            return f"No task found with ID: {todo_id}"

        if title is not None:
            todo.title = title
        if description is not None:
            todo.description = description
        if status is not None:
            todo.status = status
        if priority is not None:
            todo.priority = priority
        if due_date is not None:
            todo.due_date = due_date

        session.commit()
        session.refresh(todo)
        return f"Task with ID: {todo_id} updated successfully."
    
@tool
def delete_todo(todo_id: int):
    """
    Delete a todo task by its ID.
    
    Args:
        todo_id : The unique identifier of the task to delete (required).
    """
    with LocalSession() as session:
        todo = session.query(Todo).filter(Todo.id == todo_id).first()
        
        if not todo:
            return f"No task found with ID: {todo_id}"

        session.delete(todo)
        session.commit()
        
        return f"Task with ID: {todo_id} deleted successfully."