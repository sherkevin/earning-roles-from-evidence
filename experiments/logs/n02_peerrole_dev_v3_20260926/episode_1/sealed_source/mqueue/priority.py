"""
Priority-ordered event message wrapper.

Uses a dataclass with ordering so that events can be placed in a heap.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PriorityEvent:
    """Lower severity number = higher priority (0=critical, 9=info)

    FIX: Added a monotonic sequence counter as a deterministic, type-safe
    tie-breaker so that payloads of any type never get compared.
    """
    severity: int
    _seq: int = field(compare=True, repr=False)
    message: Any = field(compare=False)

    _counter: int = field(default=0, init=False, repr=False, compare=False)
    _counter_lock: Any = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def create(cls, severity: int, message: Any) -> 'PriorityEvent':
        """Factory method to auto-assign a unique sequence number."""
        import threading
        if cls._counter_lock is None:
            cls._counter_lock = threading.Lock()
        with cls._counter_lock:
            seq = cls._counter
            cls._counter += 1
        return cls(severity=severity, _seq=seq, message=message)
