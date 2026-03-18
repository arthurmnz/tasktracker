from app.workers.celery_app import celery_app
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task, TaskStatus
from app.services.recurrence_service import RecurrenceService
import asyncio


@celery_app.task(name='app.workers.tasks.check_recurring_tasks')
def check_recurring_tasks():
    # runs in worker sync context; create an event loop to run async DB ops
    async def _run():
        async for db in get_db():
            q = await db.execute(__import__('sqlalchemy').select(Task).where((Task.is_recurring == True) & ((Task.status == TaskStatus.DONE) | (Task.status == TaskStatus.SKIPPED))))
            tasks = q.scalars().all()
            for t in tasks:
                await RecurrenceService.generate_next_task(t, db)
            await db.commit()

    asyncio.run(_run())


@celery_app.task(name='app.workers.tasks.generate_next_occurrence')
def generate_next_occurrence(task_id: str):
    async def _run():
        async for db in get_db():
            t = await db.get(Task, task_id)
            if t:
                await RecurrenceService.generate_next_task(t, db)
                await db.commit()

    asyncio.run(_run())
