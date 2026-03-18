from fastapi import APIRouter
from .routers import auth, tasks, recurrence_rules

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(recurrence_rules.router, prefix="/recurrence-rules", tags=["recurrence-rules"])
