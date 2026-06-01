import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from database import init_db
from tools import create_todo, delete_todo, list_todos, quick_add, update_todo

init_db()

load_dotenv(".env.local")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

print("API Key Loaded:", os.getenv("GOOGLE_API_KEY") is not None)

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
"""


memory = InMemorySaver()

def createAgent():
    agent = create_agent(model=llm, tools=all_tools, checkpointer=memory )
    return agent

def call_agent(query:str):
    agent = createAgent()
    res = agent.invoke({"messages": [{"role": "user", "content": query}]}, {"configurable": {"thread_id":"1"}})

    answer = res["messages"][-1].content
    print("Agent Response:", answer)


if __name__ == "__main__":
    call_agent("List all my tasks")

