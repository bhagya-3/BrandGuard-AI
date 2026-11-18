
from datetime import datetime, timedelta, timezone
from typing import Optional


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


def add_minutes(
    minutes: int,
    start: Optional[datetime] = None,
) -> datetime:
    """Add minutes to a datetime."""
    if minutes < 0:
        raise ValueError("Minutes cannot be negative.")

    base = start or utc_now()
    return base + timedelta(minutes=minutes)


def add_hours(
    hours: int,
    start: Optional[datetime] = None,
) -> datetime:
    """Add hours to a datetime."""
    if hours < 0:
        raise ValueError("Hours cannot be negative.")

    base = start or utc_now()
    return base + timedelta(hours=hours)


def add_days(
    days: int,
    start: Optional[datetime] = None,
) -> datetime:
    """Add days to a datetime."""
    if days < 0:
        raise ValueError("Days cannot be negative.")

    base = start or utc_now()
    return base + timedelta(days=days)


def is_expired(expiry_date: Optional[datetime]) -> bool:
    """Check whether a datetime has expired."""
    if expiry_date is None:
        return True

    if expiry_date.tzinfo is None:
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)

    return expiry_date <= utc_now()


def format_datetime(
    value: Optional[datetime],
    output_format: str = "%Y-%m-%d %H:%M:%S UTC",
) -> Optional[str]:
    """Format a datetime for display."""
    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc).strftime(output_format)


def to_utc(value: datetime) -> datetime:
    """Convert a datetime to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def days_between(
    start: datetime,
    end: datetime,
) -> int:
    """Return the absolute number of complete days between two dates."""
    return abs((to_utc(end) - to_utc(start)).days)
