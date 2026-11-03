"""Defer text-only condition errors until an isolated core has finished."""
from contextvars import ContextVar
from functools import wraps


_pending = ContextVar('continuous_attacks_text_pending', default=None)


def observe_continuous_attacks(value, *, active=True):
    if isinstance(value, str) and _pending.get() is not None:
        if active() if callable(active) else active:
            _pending.set(True)
    return value


def read_continuous_attacks(scenario, *, active=True):
    return observe_continuous_attacks(scenario.get('continuous_attacks', True), active=active)


def validate_continuous_attacks(compute):
    @wraps(compute)
    def isolated(*args, **kwargs):
        token = _pending.set(False)
        try:
            result = compute(*args, **kwargs)
            if _pending.get():
                raise ValueError('continuous_attacks 不接受文本条件；请使用布尔值。')
            return result
        finally:
            _pending.reset(token)
    return isolated
