import pyodbc
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import os

# Fetch the connection string from the environment variable
connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:meharserver123.database.windows.net,1433;Database=mehardb;Uid=Useradmin;Pwd=Password@12345;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# Check if the connection string is available
if connection_string:
   print("Database connection string loaded successfully.")
else:
    print("Connection string not found in environment variables.")
    
app = FastAPI()

# Configure CORSMiddleware to allow all origins (disable CORS for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins (use '*' for development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the Task model
class Task(BaseModel):
    title: str
    description: str

# Create a table for tasks (You can run this once outside of the app)

@app.get("/")
def health():
    return {"status": "healthy"}

@app.on_event("startup")
def create_tasks_table():
    try:
        conn = pyodbc.connect(connection_string)
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
        conn.close()

        print("Tasks table verified.")

    except Exception as e:
        print(e)

# List all tasks
# @app.get("/tasks")
@app.get("/api/get")
def get_tasks():
    try:
        tasks = []

        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Tasks")

            for row in cursor.fetchall():
                tasks.append({
                    "ID": row.ID,
                    "Title": row.Title,
                    "Description": row.Description
                })

        return tasks

    except Exception as e:
        print(e)
        return {"error": str(e)}

# Retrieve a single task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Tasks WHERE ID = ?", task_id)
            row = cursor.fetchone()

            if row:
                return {
                    "ID": row.ID,
                    "Title": row.Title,
                    "Description": row.Description
                }

            return {"message": "Task not found"}

    except Exception as e:
        print(e)
        return {"error": str(e)}
