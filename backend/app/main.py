from contextlib import asynccontextmanager
import os
from typing import Dict, Generator, List

import psycopg
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://taskapp:taskapp@localhost:5432/taskapp",
)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )
        connection.commit()
    yield


app = FastAPI(title="Task Management API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TaskUpdate(BaseModel):
    completed: bool


def get_connection() -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(DATABASE_URL) as connection:
        yield connection


def serialize(row: tuple) -> Dict:
    return {"id": row[0], "title": row[1], "completed": row[2]}


@app.get("/health")
def health() -> Dict:
    return {"status": "ok"}


@app.get("/ready")
def ready(connection: psycopg.Connection = Depends(get_connection)) -> Dict:
    try:
        connection.execute("SELECT 1")
        return {"status": "ready"}
    except psycopg.Error as error:
        raise HTTPException(status_code=503, detail="database unavailable") from error


@app.get("/api/tasks")
def list_tasks(connection: psycopg.Connection = Depends(get_connection)) -> List[Dict]:
    rows = connection.execute(
        "SELECT id, title, completed FROM tasks ORDER BY id DESC"
    ).fetchall()
    return [serialize(row) for row in rows]


@app.post("/api/tasks", status_code=201)
def create_task(
    payload: TaskCreate,
    connection: psycopg.Connection = Depends(get_connection),
) -> Dict:
    row = connection.execute(
        "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, completed",
        (payload.title,),
    ).fetchone()
    connection.commit()
    return serialize(row)


@app.patch("/api/tasks/{task_id}")
def update_task(
    task_id: int,
    payload: TaskUpdate,
    connection: psycopg.Connection = Depends(get_connection),
) -> Dict:
    row = connection.execute(
        """
        UPDATE tasks
        SET completed = %s
        WHERE id = %s
        RETURNING id, title, completed
        """,
        (payload.completed, task_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="task not found")
    connection.commit()
    return serialize(row)


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    connection: psycopg.Connection = Depends(get_connection),
) -> None:
    result = connection.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="task not found")
    connection.commit()
