from uuid import UUID

from pydantic import BaseModel, ConfigDict, conint
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RecurrenceType(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"


class RecurrenceRuleCreate(BaseModel):
    type: RecurrenceType
    interval: Optional[int] = 1
    days_of_week: Optional[List[conint(ge=0, le=6)]] = None
    day_of_month: Optional[conint(ge=1, le=31)] = None
    month_of_year: Optional[conint(ge=1, le=12)] = None
    cron_expression: Optional[str] = None
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = None


class RecurrenceRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[UUID]
    user_id: Optional[UUID]
    type: RecurrenceType
    interval: int
    days_of_week: Optional[List[int]]
    day_of_month: Optional[int]
    month_of_year: Optional[int]
    cron_expression: Optional[str]
    end_date: Optional[datetime]
    max_occurrences: Optional[int]
    created_at: Optional[datetime]
