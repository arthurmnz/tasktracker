import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
import enum


class RecurrenceType(str, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"


class RecurrenceRule(Base):
    __tablename__ = "recurrence_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(Enum(RecurrenceType), nullable=False)
    interval = Column(Integer, default=1, nullable=False)
    days_of_week = Column(JSON, nullable=True)
    day_of_month = Column(Integer, nullable=True)
    month_of_year = Column(Integer, nullable=True)
    cron_expression = Column(String, nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    max_occurrences = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
