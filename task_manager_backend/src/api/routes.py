from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from .models import (
    User, UserCreate, Token, Task, TaskCreate, TaskUpdate, TaskList
)
from .utils import (
    get_current_user, verify_password, get_password_hash, create_access_token,
    fake_get_user_by_email, fake_add_user
)
from datetime import datetime
from uuid import uuid4

router = APIRouter()

# ==== User Authentication Routes ====

# PUBLIC_INTERFACE
@router.post("/auth/register", response_model=User, tags=["Authentication"], summary="Register a new user")
async def register(user_create: UserCreate):
    """Register a new user account."""
    existing = fake_get_user_by_email(user_create.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    user_id = len(fake_get_user_by_email) + 1 if callable(fake_get_user_by_email) else uuid4().int & (1<<32)-1
    hashed_password = get_password_hash(user_create.password)
    new_user = User(
        id=user_id,
        email=user_create.email,
        full_name=user_create.full_name,
        is_active=True,
    )
    fake_add_user(
        type("UserInDB", (object,), dict(**new_user.dict(), hashed_password=hashed_password))()
    )
    return new_user

# PUBLIC_INTERFACE
@router.post("/auth/login", response_model=Token, tags=["Authentication"], summary="Login a user and return JWT token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and provide JWT token."""
    user = fake_get_user_by_email(form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# ==== User Account Management ====

# PUBLIC_INTERFACE
@router.get("/users/me", response_model=User, tags=["User"], summary="Get current user info")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the currently logged-in user's info."""
    return current_user

# === Task Endpoints (CRUD + list/detail) ===

tasks_db = {}  # in-memory fake

# PUBLIC_INTERFACE
@router.post("/tasks/", response_model=Task, tags=["Tasks"], summary="Create a new task")
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    """Create a new task and assign to self or given user."""
    task_id = len(tasks_db) + 1
    now = datetime.utcnow()
    db_obj = Task(
        id=task_id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        completed=False,
        created_at=now,
        updated_at=now,
        assigned_to=task.assigned_to or current_user.id,
        creator_id=current_user.id,
    )
    tasks_db[task_id] = db_obj
    return db_obj

# PUBLIC_INTERFACE
@router.get("/tasks/", response_model=TaskList, tags=["Tasks"], summary="List all tasks")
async def list_tasks(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user)):
    """List tasks (for current user/team)."""
    filtered = [t for t in tasks_db.values() if t.assigned_to == current_user.id or t.creator_id == current_user.id]
    return TaskList(tasks=filtered[skip : skip+limit])

# PUBLIC_INTERFACE
@router.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"], summary="Get one task by ID")
async def get_task(task_id: int = Path(..., gt=0), current_user: User = Depends(get_current_user)):
    """Get single task by its ID."""
    task = tasks_db.get(task_id)
    if not task or (task.assigned_to != current_user.id and task.creator_id != current_user.id):
        raise HTTPException(404, "Task not found")
    return task

# PUBLIC_INTERFACE
@router.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"], summary="Update an existing task")
async def update_task(task_id: int, task: TaskUpdate, current_user: User = Depends(get_current_user)):
    """Update details or completion of a task."""
    db_task = tasks_db.get(task_id)
    if not db_task or (db_task.assigned_to != current_user.id and db_task.creator_id != current_user.id):
        raise HTTPException(404, "Task not found")
    update_data = task.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(db_task, k, v)
    db_task.updated_at = datetime.utcnow()
    return db_task

# PUBLIC_INTERFACE
@router.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"], summary="Delete a task")
async def delete_task(task_id: int, current_user: User = Depends(get_current_user)):
    """Delete a task by ID (allowed if creator or assignee)."""
    db_task = tasks_db.get(task_id)
    if not db_task or (db_task.assigned_to != current_user.id and db_task.creator_id != current_user.id):
        raise HTTPException(404, "Task not found or not allowed")
    del tasks_db[task_id]
    return

# PUBLIC_INTERFACE
@router.post("/tasks/{task_id}/complete", response_model=Task, tags=["Tasks"], summary="Mark a task as completed")
async def complete_task(task_id: int, current_user: User = Depends(get_current_user)):
    """Set a task as completed."""
    db_task = tasks_db.get(task_id)
    if not db_task or (db_task.assigned_to != current_user.id and db_task.creator_id != current_user.id):
        raise HTTPException(404, "Task not found or not allowed")
    db_task.completed = True
    db_task.updated_at = datetime.utcnow()
    return db_task
