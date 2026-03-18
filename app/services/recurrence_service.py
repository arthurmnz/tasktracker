from datetime import datetime, timedelta
from typing import Optional
from croniter import croniter
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recurrence_rule import RecurrenceRule, RecurrenceType
from app.models.task import Task, TaskStatus
from app.repositories.recurrence_rule_repository import RecurrenceRuleRepository
from app.repositories.task_repository import TaskRepository
from sqlalchemy import select, func
import math


class RecurrenceService:
    @staticmethod
    def calculate_next_date(rule: RecurrenceRule, from_date: datetime) -> Optional[datetime]:
        if rule.end_date and from_date and from_date >= rule.end_date:
            return None

        if rule.type == RecurrenceType.DAILY:
            return from_date + timedelta(days=rule.interval)

        if rule.type == RecurrenceType.WEEKLY:
            days = rule.days_of_week or []
            if not days:
                return None
            # find next day in the upcoming days considering interval weeks
            start = from_date + timedelta(days=1)
            for i in range(0, 7 * rule.interval):
                cand = start + timedelta(days=i)
                if cand.weekday() in days:
                    if rule.end_date and cand > rule.end_date:
                        return None
                    return cand
            return None

        if rule.type == RecurrenceType.MONTHLY:
            if not rule.day_of_month:
                return None
            year = from_date.year
            month = from_date.month
            # advance by interval months until find valid date > from_date
            for i in range(1, 1200):
                m = month + i * rule.interval
                y = year + (m - 1) // 12
                mo = ((m - 1) % 12) + 1
                try:
                    cand = datetime(y, mo, rule.day_of_month, from_date.hour, from_date.minute, from_date.second)
                except Exception:
                    continue
                if cand > from_date:
                    if rule.end_date and cand > rule.end_date:
                        return None
                    return cand
            return None

        if rule.type == RecurrenceType.YEARLY:
            if not rule.month_of_year or not rule.day_of_month:
                return None
            year = from_date.year
            for i in range(1, 100):
                y = year + i * rule.interval
                try:
                    cand = datetime(y, rule.month_of_year, rule.day_of_month, from_date.hour, from_date.minute, from_date.second)
                except Exception:
                    continue
                if cand > from_date:
                    if rule.end_date and cand > rule.end_date:
                        return None
                    return cand
            return None

        if rule.type == RecurrenceType.CUSTOM:
            if not rule.cron_expression:
                return None
            try:
                it = croniter(rule.cron_expression, from_date)
                cand = it.get_next(datetime)
                if rule.end_date and cand > rule.end_date:
                    return None
                return cand
            except Exception:
                return None

        return None

    @staticmethod
    async def should_generate_next(rule: RecurrenceRule, parent_task_id, db: AsyncSession) -> bool:
        # count existing occurrences
        q = select(func.count()).select_from(Task).where(Task.parent_task_id == parent_task_id)
        res = await db.execute(q)
        count = res.scalar() or 0
        if rule.max_occurrences is not None and count >= rule.max_occurrences:
            return False
        # calculate next date and check end_date
        now = datetime.utcnow()
        next_date = RecurrenceService.calculate_next_date(rule, now)
        if not next_date:
            return False
        if rule.end_date and next_date > rule.end_date:
            return False
        return True

    @staticmethod
    async def generate_next_task(task: Task, db: AsyncSession) -> Optional[Task]:
        if not task.is_recurring or not task.recurrence_rule_id:
            return None
        rule = await RecurrenceRuleRepository.get_by_id(db, task.recurrence_rule_id)
        if not rule:
            return None
        parent_id = task.parent_task_id or task.id
        allowed = await RecurrenceService.should_generate_next(rule, parent_id, db)
        if not allowed:
            return None
        base = task.due_date or datetime.utcnow()
        next_date = RecurrenceService.calculate_next_date(rule, base)
        if not next_date:
            return None
        new_task = Task(
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=TaskStatus.PENDING,
            priority=task.priority,
            due_date=next_date,
            is_recurring=task.is_recurring,
            recurrence_rule_id=task.recurrence_rule_id,
            parent_task_id=parent_id,
        )
        db.add(new_task)
        await db.flush()
        return new_task
