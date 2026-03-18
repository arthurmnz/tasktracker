from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .recurrence_rule import RecurrenceRuleCreate, RecurrenceRuleResponse
from enum import Enum


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    DONE = "DONE"
    SKIPPED = "SKIPPED"


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    is_recurring: Optional[bool] = False
    recurrence_rule: Optional[RecurrenceRuleCreate] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: Optional[UUID]
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    is_recurring: bool
    recurrence_rule: Optional[RecurrenceRuleResponse]
    parent_task_id: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    limit: int
