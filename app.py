import streamlit as st

from agent import createAgent
from database import LocalSession, Todo, init_db
from tools import quick_add


init_db()

st.set_page_config(page_title="AI Task Manager", page_icon="✅", layout="wide")

if "agent" not in st.session_state:
    st.session_state.agent = createAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []


def load_tasks() -> list[Todo]:
    with LocalSession() as session:
        return session.query(Todo).order_by(Todo.id.desc()).all()


def format_value(value):
    return value if value else "-"


def status_badge(status: str) -> str:
    labels = {
        "pending": "Pending",
        "in_progress": "In Progress",
        "done": "Done",
    }
    return labels.get(status, status or "Unknown")


def priority_badge(priority: str) -> str:
    labels = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
    }
    return labels.get(priority, priority or "Unknown")


def render_task_card(task: Todo) -> str:
    return f"""
    <div class="task-card">
        <div class="task-card__top">
            <div>
                <div class="task-card__id">Task #{task.id}</div>
                <div class="task-card__title">{task.title}</div>
            </div>
            <div class="task-chip task-chip--status">{status_badge(task.status)}</div>
        </div>
        <div class="task-card__meta">
            <span class="task-chip task-chip--priority">Priority: {priority_badge(task.priority)}</span>
            <span class="task-chip">Due: {format_value(task.due_date)}</span>
            <span class="task-chip">Created: {format_value(task.created_at)}</span>
        </div>
        <div class="task-card__description">{format_value(task.description)}</div>
    </div>
    """


def task_stats(tasks: list[Todo]) -> dict[str, int]:
    total = len(tasks)
    pending = len([task for task in tasks if task.status == "pending"])
    active = len([task for task in tasks if task.status == "in_progress"])
    done = len([task for task in tasks if task.status == "done"])
    return {
        "total": total,
        "pending": pending,
        "active": active,
        "done": done,
    }


st.markdown(
    """
    <style>
        :root {
            --bg: #0f172a;
            --panel: rgba(15, 23, 42, 0.78);
            --panel-strong: rgba(30, 41, 59, 0.88);
            --line: rgba(148, 163, 184, 0.18);
            --text: #e2e8f0;
            --muted: #94a3b8;
            --accent: #22c55e;
            --accent-soft: rgba(34, 197, 94, 0.14);
            --accent-2: #38bdf8;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(34, 197, 94, 0.12), transparent 24%),
                linear-gradient(180deg, #020617 0%, #0f172a 100%);
            color: var(--text);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        h1, h2, h3, p, label, span, div {
            color: var(--text);
        }

        .hero {
            border: 1px solid var(--line);
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.72));
            border-radius: 24px;
            padding: 1.4rem 1.5rem;
            box-shadow: 0 20px 60px rgba(2, 6, 23, 0.35);
            margin-bottom: 1rem;
        }

        .hero__eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.72rem;
            color: var(--accent-2);
            margin-bottom: 0.5rem;
        }

        .hero__title {
            font-size: 2.1rem;
            font-weight: 800;
            line-height: 1.05;
            margin: 0;
        }

        .hero__subtitle {
            color: var(--muted);
            margin-top: 0.45rem;
            max-width: 62ch;
        }

        .stat-card {
            border: 1px solid var(--line);
            background: rgba(15, 23, 42, 0.82);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 32px rgba(2, 6, 23, 0.18);
            height: 100%;
        }

        .stat-card__label {
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }

        .stat-card__value {
            font-size: 1.7rem;
            font-weight: 800;
            line-height: 1;
        }

        .stat-card__hint {
            color: var(--muted);
            margin-top: 0.35rem;
            font-size: 0.88rem;
        }

        .panel {
            border: 1px solid var(--line);
            background: var(--panel);
            border-radius: 24px;
            padding: 1.1rem;
            box-shadow: 0 18px 50px rgba(2, 6, 23, 0.22);
        }

        .task-card {
            border: 1px solid var(--line);
            background: var(--panel-strong);
            border-radius: 18px;
            padding: 1rem 1rem 0.95rem;
            margin-bottom: 0.9rem;
        }

        .task-card__top {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: flex-start;
            margin-bottom: 0.7rem;
        }

        .task-card__id {
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.15rem;
        }

        .task-card__title {
            font-size: 1.02rem;
            font-weight: 700;
            line-height: 1.35;
        }

        .task-card__meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-bottom: 0.7rem;
        }

        .task-card__description {
            color: var(--muted);
            line-height: 1.45;
            min-height: 1.2rem;
        }

        .task-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.28rem 0.65rem;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.12);
            border: 1px solid rgba(148, 163, 184, 0.16);
            color: var(--text);
            font-size: 0.8rem;
        }

        .task-chip--status {
            background: rgba(34, 197, 94, 0.14);
            border-color: rgba(34, 197, 94, 0.2);
        }

        .task-chip--priority {
            background: rgba(56, 189, 248, 0.14);
            border-color: rgba(56, 189, 248, 0.2);
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stChatInput"] textarea {
            border-radius: 14px !important;
            border: 1px solid rgba(148, 163, 184, 0.22) !important;
            background: rgba(15, 23, 42, 0.85) !important;
            color: var(--text) !important;
        }

        div[data-testid="stForm"] {
            border: 1px solid var(--line);
            background: rgba(15, 23, 42, 0.72);
            padding: 1rem;
            border-radius: 20px;
        }

        button[kind="primary"] {
            border-radius: 999px !important;
            font-weight: 700 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("AI Task Manager")
st.caption("Manage tasks with natural language quick add and chat-based task commands.")

tasks = load_tasks()
stats = task_stats(tasks)

st.markdown(
    """
    <div class="hero">
        <div class="hero__eyebrow">Task Control Center</div>
        <h1 class="hero__title">A cleaner way to manage tasks with natural language.</h1>
        <div class="hero__subtitle">
            Quickly add work, track progress, and chat with your task assistant from one focused dashboard.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metrics = st.columns(4, gap="small")
metric_data = [
    ("Total tasks", stats["total"], "All saved tasks in the database."),
    ("Pending", stats["pending"], "Waiting to be started."),
    ("In progress", stats["active"], "Currently being worked on."),
    ("Done", stats["done"], "Completed tasks."),
]

for column, (label, value, hint) in zip(metrics, metric_data, strict=False):
    with column:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-card__label">{label}</div>
                <div class="stat-card__value">{value}</div>
                <div class="stat-card__hint">{hint}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

left_col, right_col = st.columns([1.05, 0.95], gap="large")

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Quick Add")
    st.write("Type a task in plain English. Priority and due dates are extracted automatically when possible.")

    with st.form("quick_add_form", clear_on_submit=True):
        quick_text = st.text_input(
            "Task description",
            placeholder="Example: Buy milk tomorrow morning high priority",
            help="Try phrases like 'tomorrow', 'next Monday', or 'high priority'.",
        )
        submitted = st.form_submit_button("Add task")

    if submitted:
        if quick_text.strip():
            result = quick_add.invoke({"user_text": quick_text})
            st.success(result)
            st.rerun()
        else:
            st.warning("Enter a task description first.")

    st.divider()
    st.subheader("Task Feed")

    if not tasks:
        st.info("No tasks yet. Use Quick Add to create one.")
    else:
        for task in tasks:
            st.markdown(render_task_card(task), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Assistant Chat")
    st.caption("Ask for updates, summaries, status changes, or task lookups in plain language.")

    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])

    query = st.chat_input("Ask the assistant to manage tasks")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").markdown(query)

        response = st.session_state.agent.invoke(
            {"messages": [{"role": "user", "content": query}]},
            {"configurable": {"thread_id": "1"}},
        )
        answer = response["messages"][-1].content
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").markdown(answer)

    st.divider()
    st.subheader("How it works")
    st.markdown(
        """
        - Use natural language to add tasks quickly.
        - Priority words like `high`, `medium`, and `low` are detected automatically.
        - Dates like `tomorrow`, `next Monday`, or `25-06-2026` are parsed into due dates.
        - Task updates are saved immediately in SQLite.
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)
