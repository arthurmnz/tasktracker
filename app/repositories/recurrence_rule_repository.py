from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recurrence_rule import RecurrenceRule
from typing import Optional


class RecurrenceRuleRepository:
    @staticmethod
    async def create(session: AsyncSession, **data) -> RecurrenceRule:
        rule = RecurrenceRule(**data)
        session.add(rule)
        await session.flush()
        return rule

    @staticmethod
    async def get_by_id(session: AsyncSession, rule_id) -> Optional[RecurrenceRule]:
        q = select(RecurrenceRule).where(RecurrenceRule.id == rule_id)
        res = await session.execute(q)
        return res.scalars().first()

    @staticmethod
    async def list_by_user(session: AsyncSession, user_id) -> list[RecurrenceRule]:
        q = select(RecurrenceRule).where(RecurrenceRule.user_id == user_id)
        res = await session.execute(q)
        return res.scalars().all()

    @staticmethod
    async def update(session: AsyncSession, rule: RecurrenceRule, **patch) -> RecurrenceRule:
        for k, v in patch.items():
            setattr(rule, k, v)
        session.add(rule)
        await session.flush()
        return rule
