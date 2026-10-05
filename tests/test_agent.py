from agent import (
    _coerce_tasks,
    _extract_id,
    _generate_daily_plan,
    _generate_summary,
    create_agent,
)


def test_coerce_tasks():
    raw_list = [{"id": 1, "title": "Task 1"}, {"id": 2, "title": "Task 2"}]
    assert _coerce_tasks(raw_list) == raw_list

    raw_dict = {1: {"id": 1, "title": "Task 1"}}
    assert _coerce_tasks(raw_dict) == [{"id": 1, "title": "Task 1"}]

    assert _coerce_tasks(None) == []


def test_extract_id():
    assert _extract_id("mark task 42 as done") == 42
    assert _extract_id("delete 7") == 7
    assert _extract_id("no numbers here") is None


def test_generate_summary():
    tasks = [
        {"status": "done"},
        {"status": "pending"},
        {"status": "pending"},
        {"status": "in_progress"},
    ]
    summary = _generate_summary(tasks)
    assert summary["total"] == 4
    assert summary["done"] == 1
    assert summary["pending"] == 2
    assert summary["in_progress"] == 1
    assert summary["productivity"] == 25.0


def test_generate_daily_plan():
    tasks = [
        {"title": "High Task", "priority": "high"},
        {"title": "Med Task", "priority": "medium"},
        {"title": "Low Task", "priority": "low"},
    ]
    plan = _generate_daily_plan(tasks)
    assert len(plan["morning"]) == 1
    assert plan["morning"][0]["title"] == "High Task"
    assert len(plan["afternoon"]) == 1
    assert plan["afternoon"][0]["title"] == "Med Task"
    assert len(plan["evening"]) == 1
    assert plan["evening"][0]["title"] == "Low Task"


def test_offline_agent_fallback(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    agent = create_agent()
    res = agent.invoke({"messages": [{"role": "user", "content": "hi"}]})
    assert "messages" in res
    assert "GOOGLE_API_KEY" in res["messages"][0].content


def test_get_checkpointer_sqlite(tmp_path):
    from langgraph.checkpoint.sqlite import SqliteSaver

    from agent import get_checkpointer

    db_path = str(tmp_path / "checkpoints.db")
    saver = get_checkpointer(db_path)
    assert isinstance(saver, SqliteSaver)


def test_checkpointer_persistence_and_isolation(tmp_path):
    import sqlite3

    from langgraph.checkpoint.sqlite import SqliteSaver

    from agent import get_checkpointer

    db_path = str(tmp_path / "isolated.db")
    saver = get_checkpointer(db_path)
    assert isinstance(saver, SqliteSaver)

    # Verify tables created
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    assert "checkpoints" in tables

    # Test re-opening the same DB file retains schema
    saver2 = get_checkpointer(db_path)
    assert isinstance(saver2, SqliteSaver)


def test_create_agent_checkpointer_binding(tmp_path):
    from agent import create_agent, get_checkpointer

    custom_saver = get_checkpointer(str(tmp_path / "custom.db"))
    agent = create_agent(checkpointer=custom_saver)
    assert hasattr(agent, "checkpointer")
    assert agent.checkpointer is custom_saver
