from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.core.dependencies import get_db_dep, get_current_user
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse, TaskUpdate
from app.services.task_service import TaskService
from app.repositories.task_repository import TaskRepository
from app.models.task import Task as TaskModel
from sqlalchemy import select

router = APIRouter()


@router.get('/', response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    is_recurring: Optional[bool] = None,
    due_date_from: Optional[datetime] = None,
    due_date_to: Optional[datetime] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = 'created_at',
    order: str = 'desc',
    db: AsyncSession = Depends(get_db_dep),
    user=Depends(get_current_user),
):
    filters = {}
    if status:
        filters['status'] = status
    if priority:
        filters['priority'] = priority
    if is_recurring is not None:
        filters['is_recurring'] = is_recurring
    if due_date_from:
        filters['due_date_from'] = due_date_from
    if due_date_to:
        filters['due_date_to'] = due_date_to
    offset = (page - 1) * limit
    items, total = await TaskRepository.list_by_user(db, user.id, filters=filters, offset=offset, limit=limit)
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get('/upcoming', response_model=list[TaskResponse])
async def upcoming(days: int = Query(7, ge=1), db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    items = await TaskRepository.list_upcoming(db, user.id, days)
    return items


@router.get('/overdue', response_model=list[TaskResponse])
async def overdue(db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    items = await TaskRepository.list_overdue(db, user.id)
    return items


@router.get('/{task_id}', response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    task = await TaskService.get(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')
    return task


@router.get('/{task_id}/history', response_model=list[TaskResponse])
async def task_history(task_id: str, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    t = await TaskRepository.get_by_id(db, task_id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')
    root = t.parent_task_id or t.id
    res = await db.execute(select(TaskModel).where(TaskModel.parent_task_id == root))
    return res.scalars().all()


@router.post('/', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    try:
        task = await TaskService.create(db, user.id, payload)
        return task
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.patch('/{task_id}', response_model=TaskResponse)
async def update_task(task_id: str, patch: TaskUpdate, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    task = await TaskService.update(db, user.id, task_id, patch)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')
    await db.commit()
    return task


@router.delete('/{task_id}')
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    res = await TaskService.delete(db, user.id, task_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')
    await db.commit()
    return {"ok": True}


@router.post('/{task_id}/complete', response_model=TaskResponse)
async def complete_task(task_id: str, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    task = await TaskService.complete(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')
    await db.commit()
    return task


@router.post('/{task_id}/skip', response_model=TaskResponse)
async def skip_task(task_id: str, db: AsyncSession = Depends(get_db_dep), user=Depends(get_current_user)):
    task = await TaskService.skip(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')
    await db.commit()
    return task
