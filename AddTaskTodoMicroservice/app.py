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


# Health endpoint (used by Application Gateway)
@app.get("/api/create")
def health():
    return {"status": "healthy"}

@app.get("/")
def health():
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


# Create Task
@app.post("/api/create")
def create_task(task: Task):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO Tasks (Title, Description) VALUES (?, ?)",
                task.title,
                task.description
            )

            conn.commit()

        return {
            "message": "Task created successfully",
            "task": task
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))