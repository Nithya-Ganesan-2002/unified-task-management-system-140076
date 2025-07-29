from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(..., description="The user's email address")
    password: str = Field(..., min_length=6, description="User password")
    full_name: Optional[str] = Field(None, description="Full name of the user")

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="The user's email address")
    password: str = Field(..., min_length=6, description="User password")

# PUBLIC_INTERFACE
class User(BaseModel):
    """Response model for user information."""
    id: int
    email: EmailStr
    full_name: Optional[str]
    is_active: bool

# PUBLIC_INTERFACE
class UserInDB(User):
    """Internal user model for DB integration."""
    hashed_password: str

# PUBLIC_INTERFACE
class Token(BaseModel):
    """Model for authentication token responses."""
    access_token: str
    token_type: str

# PUBLIC_INTERFACE
class TokenData(BaseModel):
    """Optional data within a JWT token."""
    user_id: Optional[int] = None

# PUBLIC_INTERFACE
class TaskBase(BaseModel):
    """Base model for tasks."""
    title: str = Field(..., max_length=128)
    description: Optional[str] = Field(None, max_length=4096)
    due_date: Optional[datetime]
    assigned_to: Optional[int] = Field(None, description="User ID")    

# PUBLIC_INTERFACE
class TaskCreate(TaskBase):
    """Request model for creating a task."""
    pass

# PUBLIC_INTERFACE
class TaskUpdate(TaskBase):
    """Request/Model for updating a task."""
    completed: Optional[bool] = None

# PUBLIC_INTERFACE
class Task(TaskBase):
    """Response model for tasks."""
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime
    creator_id: int

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class TaskList(BaseModel):
    """Model for returning a list of tasks."""
    tasks: List[Task]
