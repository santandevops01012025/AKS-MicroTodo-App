import os
import pyodbc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Fetch the connection string from environment variable
connection_string = os.environ.get("CONNECTION_STRING")

if connection_string:
    print("Database connection string loaded successfully.")
else:
    print("Connection string not found in environment variables.")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task model
class Task(BaseModel):
    title: str
    description: str


# Health endpoint for AGIC probe
@app.get("/api/delete")
def delete_health():
    return {"status": "healthy"}


# Root health endpoint
@app.get("/")
def root_health():
    return {"status": "healthy"}


# Create table during application startup
@app.on_event("startup")
def create_tasks_table():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            cursor.execute("""
            IF OBJECT_ID('Tasks', 'U') IS NULL
            BEGIN
                CREATE TABLE Tasks (
                    ID INT IDENTITY PRIMARY KEY,
                    Title VARCHAR(255),
                    Description TEXT
                )
            END
            """)

            conn.commit()

        print("Tasks table verified.")

    except Exception as e:
        print(e)


# Delete Task
@app.delete("/api/delete/{task_id}")
def delete_task(task_id: int):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM Tasks WHERE ID = ?",
                task_id
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Task not found"
                )

            conn.commit()

        return {
            "message": "Task deleted successfully",
            "task_id": task_id
        }

    except HTTPException:
        raise

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )