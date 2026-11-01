from __future__ import annotations
from datetime import datetime, timedelta


_ATTEMPTS: dict[str, list[datetime]] = {}
WINDOW = timedelta(minutes=10)
MAX_ATTEMPTS = 5
BLOCK = timedelta(minutes=5)




def is_blocked(key: str) -> bool:
    now = datetime.now()
    recent = [t for t in _ATTEMPTS.get(key, []) if now - t <= WINDOW]
    _ATTEMPTS[key] = recent
    return len(recent) >= MAX_ATTEMPTS and now - recent[-MAX_ATTEMPTS] <= BLOCK




def register_failure(key: str) -> None:
    _ATTEMPTS.setdefault(key, []).append(datetime.now())




def clear_failures(key: str) -> None:
    _ATTEMPTS.pop(key, None)
