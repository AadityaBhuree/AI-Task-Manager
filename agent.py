import os
import re
from datetime import datetime, timedelta
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from database import init_db
from tools import create_todo, delete_todo, list_todos, quick_add, update_todo

init_db()

load_dotenv(".env.local")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class _OfflineMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _OfflineAgent:
    def invoke(self, *args: Any, **kwargs: Any) -> dict[str, list[_OfflineMessage]]:
        return {
            "messages": [
                _OfflineMessage(
                    "Set GOOGLE_API_KEY in the deployment environment to enable the assistant."
                )
            ]
        }


def _build_llm() -> ChatGoogleGenerativeAI:
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is missing.")

    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

all_tools = [create_todo, quick_add, list_todos, update_todo, delete_todo]

system_prompt = """ You are smart and friendly Todo assistant. You can help users manage their tasks effectively.
You help users manage their tasks using database. You can
- Create new tasks with a title, description, priority, and due date.
- List existing tasks with optional filters for status and priority.
- Update task details, including status and priority.
- Delete tasks by their ID.

-GUIDELINES:
-Always confirm what action you took after each tool call.
-When listing todos , present them in a readable table format.
-"mark as done" --> update the task's status to "done"
-"start working on" --> update the task's status to "in_progress"
-"show pending" --> list tasks with status "pending"
-"high priority" --> list tasks with priority "high"
- Be concise and clear in your responses. Avoid unnecessary details.

Status values: 'pending'| 'in_progress'|'done'

Use Status Icons with status values:
- pending: 🕒 Pending
- in_progress: 🕒 In Progress
- done: ✅ Done
Priority values: 'low'| 'medium'| 'high'
Use Priority Icons with priority values:
- low: 🟢 Low
- medium: 🟡 Medium
- high: 🔴 High

Behavior rules:
- Prefer the task tools when the user asks to create, list, update, or delete tasks.
- If a user asks for a summary, count tasks by status and keep the result concise.
- If a user asks to plan the day, group high-priority tasks first, then medium, then low.
- When you mention tasks, include the task ID when available.
- Keep responses short, actionable, and easy to scan.
"""


memory = InMemorySaver()

def createAgent():
    if not GOOGLE_API_KEY:
        return _OfflineAgent()

    llm = _build_llm()
    agent = create_agent(
        model=llm,
        tools=all_tools,
        system_prompt=system_prompt,
        checkpointer=memory,
    )
    return agent


def _coerce_tasks(raw_tasks: Any) -> list[dict[str, Any]]:
    if isinstance(raw_tasks, dict):
        values = raw_tasks.values()
    elif isinstance(raw_tasks, list):
        values = raw_tasks
    else:
        values = []

    tasks: list[dict[str, Any]] = []
    for task in values:
        if hasattr(task, "to_dict"):
            tasks.append(task.to_dict())
        elif isinstance(task, dict):
            tasks.append(task)
    return tasks


def _extract_id(query: str) -> int | None:
    match = re.search(r"\d+", query)
    return int(match.group()) if match else None


def _generate_summary(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(tasks)
    done = len([task for task in tasks if task.get("status") == "done"])
    pending = len([task for task in tasks if task.get("status") == "pending"])
    in_progress = len([task for task in tasks if task.get("status") == "in_progress"])
    productivity = round((done / total) * 100, 2) if total else 0
    return {
        "total": total,
        "done": done,
        "pending": pending,
        "in_progress": in_progress,
        "productivity": productivity,
    }


def _generate_daily_plan(tasks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    plan = {"morning": [], "afternoon": [], "evening": []}
    priority_slots = {"high": "morning", "medium": "afternoon", "low": "evening"}

    for task in tasks:
        slot = priority_slots.get(task.get("priority", "medium"), "afternoon")
        plan[slot].append(task)

    return plan

def call_agent(query:str):
    agent = createAgent()

    lowered = query.lower()
    if "summary" in lowered or "report" in lowered:
        tasks = _coerce_tasks(list_todos.invoke({}))
        summary = _generate_summary(tasks)
        print("Agent Response:", summary)
        return

    if "plan my day" in lowered or "daily plan" in lowered:
        tasks = _coerce_tasks(list_todos.invoke({}))
        plan = _generate_daily_plan(tasks)
        print("Agent Response:", plan)
        return

    if any(word in lowered for word in ["mark", "done", "complete"]):
        task_id = _extract_id(query)
        if task_id is not None:
            result = update_todo.invoke({"todo_id": task_id, "status": "done"})
            print("Agent Response:", result)
            return

    res = agent.invoke({"messages": [{"role": "user", "content": query}]}, {"configurable": {"thread_id":"1"}})

    answer = res["messages"][-1].content
    print("Agent Response:", answer)


if __name__ == "__main__":
    call_agent("List all my tasks")

