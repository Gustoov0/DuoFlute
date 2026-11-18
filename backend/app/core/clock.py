from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.core.config import settings


def local_tz() -> ZoneInfo:
    return ZoneInfo(settings.timezone)


def today_local() -> date:
    """Data de 'hoje' no fuso configurado (e não em UTC)."""
    return datetime.now(local_tz()).date()