from fastapi import APIRouter

from . import healthz, chat

__all__ = ["router"]

router = APIRouter()

# modules = [healthz, exercise, chat, user, history, config, file, course, task, task_exercise]
modules = [chat]

for module in modules:
    router.include_router(module.router)
