from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from starlette.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).parent


def datetime_filter(value: str | float | datetime):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            value = value.astimezone(tz=timezone.utc)
    if isinstance(value, float):
        value = datetime.fromtimestamp(value, tz=timezone.utc)
    return value.strftime("%d %B %Y %H:%M")


templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["datetime"] = datetime_filter
