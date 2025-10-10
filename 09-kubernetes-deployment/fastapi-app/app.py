#!/usr/bin/env python3
"""
FastAPI Task Manager - Kubernetes Version
A containerized REST API for managing tasks.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
import os


app = FastAPI(title="Task Manager API", version="1.0.0")


# Data models
class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: str
    updated_at: str


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


# In-memory storage
tasks_db: dict[int, Task] = {
    1: Task(
        id=1,
        title="Example Task",
        description="This is a sample task",
        completed=False,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
}
next_task_id = 2


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Task Manager API",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "production"),
        "endpoints": {
            "tasks": "/tasks",
            "task": "/tasks/{task_id}",
            "stats": "/stats",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/tasks", response_model=List[Task])
async def list_tasks(completed: Optional[bool] = None):
    """List all tasks, optionally filtered by completion status."""
    if completed is None:
        return list(tasks_db.values())
    
    return [task for task in tasks_db.values() if task.completed == completed]


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    """Get a specific task by ID."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]


@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(task: TaskCreate):
    """Create a new task."""
    global next_task_id
    
    now = datetime.now().isoformat()
    new_task = Task(
        id=next_task_id,
        title=task.title,
        description=task.description,
        completed=False,
        created_at=now,
        updated_at=now
    )
    
    tasks_db[next_task_id] = new_task
    next_task_id += 1
    
    return new_task


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.completed is not None:
        task.completed = task_update.completed
    
    task.updated_at = datetime.now().isoformat()
    
    return task


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete a task."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    deleted_task = tasks_db.pop(task_id)
    return {"message": "Task deleted", "task": deleted_task}


@app.get("/stats")
async def get_stats():
    """Get task statistics."""
    total = len(tasks_db)
    completed = sum(1 for task in tasks_db.values() if task.completed)
    pending = total - completed
    
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "completion_rate": f"{(completed / total * 100):.1f}%" if total > 0 else "0%"
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Task Manager API on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
