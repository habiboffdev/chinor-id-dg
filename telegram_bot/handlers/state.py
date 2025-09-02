# Simple in-memory state for MVP. Replace with Redis/DB later.
from typing import Dict

_user_lang: Dict[int, str] = {}


def get_lang(user_id: int) -> str | None:
    return _user_lang.get(user_id)


def set_lang(user_id: int, lang: str) -> None:
    _user_lang[user_id] = lang
