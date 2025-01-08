from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    validates,
    declarative_mixin,
    orm_insert_sentinel,
    declared_attr,
)

from src.types import DateTimeUTC
# ruff: noqa: FA100


@declarative_mixin
class SentinelMixin:
    """Mixin to add a sentinel column for SQLAlchemy models."""

    @declared_attr
    def _sentinel(cls) -> Mapped[int]:
        return orm_insert_sentinel(name="sa_orm_sentinel")


@declarative_mixin
class AuditColumns:
    """Created/Updated At Fields Mixin."""

    created_at: Mapped[datetime] = mapped_column(
        DateTimeUTC(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    """Date/time of instance creation."""
    updated_at: Mapped[datetime] = mapped_column(
        DateTimeUTC(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    """Date/time of instance last update."""

    @validates("created_at", "updated_at")
    def validate_tz_info(self, _: str, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


@declarative_mixin
class UUIDPrimaryKey(SentinelMixin):
    """UUID Primary Key Field Mixin."""

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    """UUID Primary key column."""
