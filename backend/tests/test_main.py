from contextlib import contextmanager

from fastapi.testclient import TestClient
import psycopg

from app.main import app, get_connection


class FakeResult:
    def __init__(self, rows=None, rowcount=0):
        self._rows = rows or []
        self.rowcount = rowcount

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows


class FakeDatabase:
    def __init__(self):
        self.tasks = {}
        self.next_id = 1


class FakeConnection:
    def __init__(self, database):
        self.database = database

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        normalized_query = " ".join(query.split()).lower()

        if normalized_query == "select 1":
            return FakeResult([(1,)])

        if "create table if not exists tasks" in normalized_query:
            return FakeResult()

        if normalized_query.startswith("select id, title, completed from tasks order by id desc"):
            rows = [
                (task_id, task["title"], task["completed"])
                for task_id, task in sorted(self.database.tasks.items(), reverse=True)
            ]
            return FakeResult(rows)

        if normalized_query.startswith("insert into tasks (title) values (%s) returning id, title, completed"):
            title = params[0]
            task_id = self.database.next_id
            self.database.next_id += 1
            task = {"title": title, "completed": False}
            self.database.tasks[task_id] = task
            return FakeResult([(task_id, task["title"], task["completed"])])

        if normalized_query.startswith("update tasks set completed = %s where id = %s returning id, title, completed"):
            completed, task_id = params
            task = self.database.tasks.get(task_id)
            if task is None:
                return FakeResult([])
            task["completed"] = completed
            return FakeResult([(task_id, task["title"], task["completed"])])

        if normalized_query.startswith("delete from tasks where id = %s"):
            task_id = params[0]
            removed = self.database.tasks.pop(task_id, None)
            return FakeResult(rowcount=1 if removed is not None else 0)

        raise AssertionError(f"unexpected query: {query}")

    def commit(self):
        return None


@contextmanager
def make_client():
    database = FakeDatabase()
    original_connect = psycopg.connect

    def fake_connect(_: str):
        return FakeConnection(database)

    psycopg.connect = fake_connect
    app.dependency_overrides[get_connection] = lambda: FakeConnection(database)

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        psycopg.connect = original_connect


def test_health_endpoint():
    with make_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint():
    with make_client() as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_task_lifecycle():
    with make_client() as client:
        create_response = client.post("/api/tasks", json={"title": "Write CI pipeline"})
        assert create_response.status_code == 201

        task = create_response.json()
        assert task == {"id": 1, "title": "Write CI pipeline", "completed": False}

        list_response = client.get("/api/tasks")
        assert list_response.status_code == 200
        assert list_response.json() == [task]

        update_response = client.patch(f"/api/tasks/{task['id']}", json={"completed": True})
        assert update_response.status_code == 200
        assert update_response.json() == {"id": 1, "title": "Write CI pipeline", "completed": True}

        delete_response = client.delete(f"/api/tasks/{task['id']}")
        assert delete_response.status_code == 204

        missing_response = client.delete(f"/api/tasks/{task['id']}")
        assert missing_response.status_code == 404