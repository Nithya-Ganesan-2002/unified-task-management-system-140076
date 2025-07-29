from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

openapi_tags = [
    {"name": "Authentication", "description": "User registration and login."},
    {"name": "Tasks", "description": "Task CRUD, listing, and completion."},
    {"name": "User", "description": "Account management and profile."},
]

app = FastAPI(
    title="Task Manager API",
    description="Backend service for user/task management, authentication, and dashboard subsystem.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"message": "Healthy"}

