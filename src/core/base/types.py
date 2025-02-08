# ruff: noqa: FA100
import datetime
import re
from typing import Optional, Type

from sqlalchemy import DateTime, BigInteger
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator


class DateTimeUTC(TypeDecorator[datetime.datetime]):
    """Timezone Aware DateTime.

    Ensure UTC is stored in the database and that TZ aware dates are returned for all dialects.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    @property
    def python_type(self) -> Type[datetime.datetime]:
        return datetime.datetime

    def process_bind_param(
        self, value: Optional[datetime.datetime], dialect: Dialect
    ) -> Optional[datetime.datetime]:
        if value is None:
            return value
        if not value.tzinfo:
            msg = "tzinfo is required"
            raise TypeError(msg)
        return value.astimezone(datetime.timezone.utc)

    def process_result_value(
        self, value: Optional[datetime.datetime], dialect: Dialect
    ) -> Optional[datetime.datetime]:
        if value is None:
            return value
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value


class DigitsOnlyInteger(TypeDecorator[int]):
    """
    Custom type that strips non-digit characters from a string and converts it to an integer.
    """

    impl = BigInteger  # The underlying database type
    cache_ok = True

    def process_bind_param(self, value: str, dialect: Dialect) -> int:
        """Process the value before storing it in the database."""
        # Remove all non-digit characters and convert to integer
        return int(re.sub(r"[^0-9]", "", value))

    def process_result_value(self, value: int, dialect: Dialect) -> int:
        """Process the value when loading it from the database."""
        return value  # No processing needed when retrieving from the database
