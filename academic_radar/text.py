import html
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime


def clean_text(value):
    if not value:
        return ""
    value = html.unescape(str(value))
    value = re.sub(r"<.*?>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_feed_date(entry):
    for key in ["published", "updated", "created"]:
        value = entry.get(key)
        if not value:
            continue
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    return None


def too_old(dt, max_age_days):
    if not dt:
        return False
    return dt < datetime.now(timezone.utc) - timedelta(days=max_age_days)
