from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv

try:
    from langchain.agents import create_agent as lc_create_agent
except ImportError:
    try:
        from langgraph.prebuilt import create_react_agent as lc_create_agent
    except ImportError:
        lc_create_agent = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

from langgraph.checkpoint.memory import InMemorySaver

from database import init_db
from tools import create_todo, delete_todo, list_todos, quick_add, update_todo

init_db()

load_dotenv(".env.local")
load_dotenv(".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class _OfflineMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _OfflineAgent:
    def invoke(self, *args: Any, **kwargs: Any) -> dict[str, list[_OfflineMessage]]:
        return {
            "messages": [
                _OfflineMessage(
                    "Set GOOGLE_API_KEY in environment to enable full assistant capabilities."
                )
            ]
        }


def _build_llm() -> Any:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or not ChatGoogleGenerativeAI:
        raise RuntimeError("GOOGLE_API_KEY is missing or langchain_google_genai not installed.")

    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)


ALL_TOOLS = [create_todo, quick_add, list_todos, update_todo, delete_todo]

SYSTEM_PROMPT = """You are a smart and friendly Todo assistant. You help users manage their tasks effectively.

You can:
- Create new tasks with a title, description, priority ('low', 'medium', 'high'), and due date.
- List existing tasks with optional filters for status ('pending', 'in_progress', 'done') and priority.
- Update task details, including status and priority.
- Delete tasks by their ID.

GUIDELINES:
- Always confirm what action you took after each tool call.
- When listing todos, present them in a readable format.
- Status values: 'pending' (🕒 Pending), 'in_progress' (🔄 In Progress), 'done' (✅ Done).
- Priority values: 'low' (🟢 Low), 'medium' (🟡 Medium), 'high' (🔴 High).
- Keep responses short, clear, actionable, and easy to scan. Include task IDs when referring to tasks.
"""

memory = InMemorySaver()


def create_agent() -> Any:
    """Factory function to build and configure the LangChain/LangGraph agent."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here" or lc_create_agent is None:
        return _OfflineAgent()

    try:
        llm = _build_llm()
        return lc_create_agent(
            model=llm,
            tools=ALL_TOOLS,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=memory,
        )
    except Exception:
        return _OfflineAgent()


# Backwards compatibility alias
createAgent = create_agent


def _coerce_tasks(raw_tasks: Any) -> list[dict[str, Any]]:
    """Normalize tool outputs into a list of task dictionaries."""
    if isinstance(raw_tasks, list):
        return [t for t in raw_tasks if isinstance(t, dict)]
    if isinstance(raw_tasks, dict):
        return list(raw_tasks.values())
    return []


def _extract_id(query: str) -> int | None:
    """Extract first integer ID from natural language query."""
    match = re.search(r"\b\d+\b", query)
    return int(match.group()) if match else None


def _generate_summary(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate summary statistics for a set of tasks."""
    total = len(tasks)
    done = len([task for task in tasks if task.get("status") == "done"])
    pending = len([task for task in tasks if task.get("status") == "pending"])
    in_progress = len([task for task in tasks if task.get("status") == "in_progress"])
    productivity = round((done / total) * 100, 2) if total > 0 else 0.0

    return {
        "total": total,
        "done": done,
        "pending": pending,
        "in_progress": in_progress,
        "productivity": productivity,
    }


def _generate_daily_plan(tasks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Organize tasks into morning, afternoon, and evening slots based on priority."""
    plan: dict[str, list[dict[str, Any]]] = {"morning": [], "afternoon": [], "evening": []}
    priority_slots = {"high": "morning", "medium": "afternoon", "low": "evening"}

    for task in tasks:
        slot = priority_slots.get(task.get("priority", "medium"), "afternoon")
        plan[slot].append(task)

    return plan


def call_agent(query: str) -> str | dict[str, Any]:
    """Command-line entry point to invoke agent or helper actions."""
    agent = create_agent()

    lowered = query.lower()

    if "summary" in lowered or "report" in lowered:
        raw = list_todos.invoke({})
        tasks = _coerce_tasks(raw)
        summary = _generate_summary(tasks)
        print("Agent Response:", summary)
        return summary

    if "plan my day" in lowered or "daily plan" in lowered:
        raw = list_todos.invoke({})
        tasks = _coerce_tasks(raw)
        plan = _generate_daily_plan(tasks)
        print("Agent Response:", plan)
        return plan

    if any(word in lowered for word in ["mark", "complete"]) and "done" in lowered:
        task_id = _extract_id(query)
        if task_id is not None:
            result = update_todo.invoke({"todo_id": task_id, "status": "done"})
            print("Agent Response:", result)
            return str(result)

    res = agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        {"configurable": {"thread_id": "1"}},
    )

    answer = res["messages"][-1].content
    print("Agent Response:", answer)
    return str(answer)


if __name__ == "__main__":
    call_agent("List all my tasks")
