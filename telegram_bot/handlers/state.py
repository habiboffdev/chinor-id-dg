# Thread-safe in-memory state for MVP. Replace with Redis/DB later.
import threading
from typing import Dict

_user_lang: Dict[int, str] = {}
_lang_lock = threading.Lock()


def get_lang(user_id: int) -> str | None:
    """Thread-safe language retrieval"""
    with _lang_lock:
        return _user_lang.get(user_id)


def set_lang(user_id: int, lang: str) -> None:
    """Thread-safe language setting"""
    with _lang_lock:
        _user_lang[user_id] = lang


def clear_lang(user_id: int) -> None:
    """Clear language state to prevent memory leaks"""
    with _lang_lock:
        _user_lang.pop(user_id, None)
