from fastapi import FastAPI
from router.auth_routes import router as auth_router
from router.project_routes import router as project_router
from router.task_routes import router as task_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)