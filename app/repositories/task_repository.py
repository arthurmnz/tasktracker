from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from typing import Optional
from datetime import datetime

class TaskRepository:
    @staticmethod
    async def create(session: AsyncSession, **data) -> Task:
        task = Task(**data)
        session.add(task)
        await session.flush()
        # recarrega com o relationship
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.recurrence_rule))
            .where(Task.id == task.id)
        )
        return result.scalar_one()

    @staticmethod
    async def get_by_id(session: AsyncSession, task_id) -> Optional[Task]:
        q = select(Task).options(selectinload(Task.recurrence_rule)).where(Task.id == task_id)
        res = await session.execute(q)
        return res.scalars().first()

    @staticmethod
    async def list_by_user(session: AsyncSession, user_id, filters: dict = None, offset: int = 0, limit: int = 20):
        q = select(Task).options(selectinload(Task.recurrence_rule)).where(Task.user_id == user_id)
        if filters:
            if 'status' in filters:
                q = q.where(Task.status == filters['status'])
            if 'priority' in filters:
                q = q.where(Task.priority == filters['priority'])
            if 'is_recurring' in filters:
                q = q.where(Task.is_recurring == filters['is_recurring'])
            if 'due_date_from' in filters:
                q = q.where(Task.due_date >= filters['due_date_from'])
            if 'due_date_to' in filters:
                q = q.where(Task.due_date <= filters['due_date_to'])
        total_res = await session.execute(select(Task.id).where(Task.user_id == user_id))
        total = len(total_res.scalars().all())
        res = await session.execute(q.offset(offset).limit(limit))
        items = res.scalars().all()
        return items, total

    @staticmethod
    async def list_upcoming(session: AsyncSession, user_id, days: int):
        from datetime import timedelta
        now = datetime.utcnow()
        end = now + timedelta(days=days)
        q = select(Task).options(selectinload(Task.recurrence_rule)).where(
            and_(Task.user_id == user_id, Task.due_date != None, Task.due_date <= end)
        )
        res = await session.execute(q)
        return res.scalars().all()

    @staticmethod
    async def list_overdue(session: AsyncSession, user_id):
        now = datetime.utcnow()
        q = select(Task).options(selectinload(Task.recurrence_rule)).where(
            and_(Task.user_id == user_id, Task.due_date != None, Task.due_date < now, Task.status != 'DONE')
        )
        res = await session.execute(q)
        return res.scalars().all()

    @staticmethod
    async def update(session: AsyncSession, task: Task, **patch) -> Task:
        for k, v in patch.items():
            setattr(task, k, v)
        session.add(task)
        await session.flush()
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.recurrence_rule))
            .where(Task.id == task.id)
        )
        return result.scalar_one()

    @staticmethod
    async def delete(session: AsyncSession, task: Task):
        await session.delete(task)
        await session.flush()