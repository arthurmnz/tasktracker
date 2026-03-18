from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_dep, get_current_user
from app.repositories.recurrence_rule_repository import RecurrenceRuleRepository
from app.schemas.recurrence_rule import RecurrenceRuleCreate, RecurrenceRuleResponse

router = APIRouter()


@router.get('/', response_model=list[RecurrenceRuleResponse])
async def list_rules(db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    rules = await RecurrenceRuleRepository.list_by_user(db, user.id)
    return rules


@router.post('/', response_model=RecurrenceRuleResponse)
async def create_rule(payload: RecurrenceRuleCreate, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    # validations
    if payload.type.name == 'WEEKLY' and (not payload.days_of_week or len(payload.days_of_week) == 0):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='days_of_week required for WEEKLY')
    if payload.type.name == 'MONTHLY' and not payload.day_of_month:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='day_of_month required for MONTHLY')
    if payload.max_occurrences and payload.end_date:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='max_occurrences and end_date are mutually exclusive')
    if payload.type.name == 'CUSTOM' and payload.cron_expression:
        from croniter import croniter
        if not croniter.is_valid(payload.cron_expression):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid cron expression')

    data = payload.model_dump()
    data['user_id'] = user.id
    rule = await RecurrenceRuleRepository.create(db, **data)
    await db.commit()
    return rule


@router.get('/{rule_id}', response_model=RecurrenceRuleResponse)
async def get_rule(rule_id: str, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    rule = await RecurrenceRuleRepository.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    if str(rule.user_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return rule


@router.patch('/{rule_id}', response_model=RecurrenceRuleResponse)
async def update_rule(rule_id: str, payload: RecurrenceRuleCreate, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    rule = await RecurrenceRuleRepository.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    if str(rule.user_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    updated = await RecurrenceRuleRepository.update(db, rule, **payload.model_dump(exclude_none=True))
    await db.commit()
    return updated


@router.delete('/{rule_id}')
async def delete_rule(rule_id: str, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    rule = await RecurrenceRuleRepository.get_by_id(db, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    if str(rule.user_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    # unlink tasks
    from app.repositories.task_repository import TaskRepository
    tasks = await TaskRepository.list_by_user(db, user.id)
    for t in tasks[0]:
        if t.recurrence_rule_id and str(t.recurrence_rule_id) == str(rule.id):
            t.recurrence_rule_id = None
            t.is_recurring = False
            db.add(t)
    await db.flush()
    # delete rule
    await db.delete(rule)
    await db.commit()
    return {"ok": True}
