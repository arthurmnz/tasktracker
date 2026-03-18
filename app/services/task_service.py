from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.repositories.recurrence_rule_repository import RecurrenceRuleRepository
from app.services.recurrence_service import RecurrenceService
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from typing import Optional


class TaskService:
    @staticmethod
    async def create(session: AsyncSession, user_id, payload: TaskCreate) -> Task:
        data = payload.model_dump()
        recurrence_rule = data.pop('recurrence_rule', None)
        if data.get('is_recurring') and not recurrence_rule:
            raise ValueError('is_recurring requires recurrence_rule')

        rule_obj = None
        if recurrence_rule:
            recurrence_rule['user_id'] = user_id
            if isinstance(recurrence_rule, dict):
                rule_obj = await RecurrenceRuleRepository.create(session, **recurrence_rule)
            else:
                rule_obj = await RecurrenceRuleRepository.create(session, **recurrence_rule.model_dump())
        task = await TaskRepository.create(session, user_id=user_id, recurrence_rule_id=(rule_obj.id if rule_obj else None), **data)
        return task

    @staticmethod
    async def get(session: AsyncSession, user_id, task_id) -> Optional[Task]:
        task = await TaskRepository.get_by_id(session, task_id)
        if not task:
            return None
        if str(task.user_id) != str(user_id):
            raise PermissionError()
        return task

    @staticmethod
    async def update(session: AsyncSession, user_id, task_id, patch: TaskUpdate) -> Optional[Task]:
        task = await TaskRepository.get_by_id(session, task_id)
        if not task:
            return None
        if str(task.user_id) != str(user_id):
            raise PermissionError()
        updated = await TaskRepository.update(session, task, **patch.model_dump(exclude_none=True))
        return updated

    @staticmethod
    async def delete(session: AsyncSession, user_id, task_id):
        task = await TaskRepository.get_by_id(session, task_id)
        if not task:
            return None
        if str(task.user_id) != str(user_id):
            raise PermissionError()
        await TaskRepository.delete(session, task)
        return True

    @staticmethod
    async def complete(session: AsyncSession, user_id, task_id):
        task = await TaskRepository.get_by_id(session, task_id)
        if not task:
            return None
        if str(task.user_id) != str(user_id):
            raise PermissionError()
        task.status = TaskStatus.DONE
        task.completed_at = datetime.utcnow()
        await session.flush()
        # generate next occurrence if recurring
        if task.is_recurring:
            await RecurrenceService.generate_next_task(task, session)
        return task

    @staticmethod
    async def skip(session: AsyncSession, user_id, task_id):
        task = await TaskRepository.get_by_id(session, task_id)
        if not task:
            return None
        if str(task.user_id) != str(user_id):
            raise PermissionError()
        task.status = TaskStatus.SKIPPED
        task.completed_at = datetime.utcnow()
        await session.flush()
        if task.is_recurring:
            await RecurrenceService.generate_next_task(task, session)
        return task
