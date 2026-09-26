"""
Priority-ordered task message wrapper.

Uses a dataclass with ordering so that tasks can be placed in a heap.
A deterministic, type-safe tie-breaker (sequence number) is used for
equal-priority messages to avoid comparing arbitrary payload types.
"""
import itertools
from dataclasses import dataclass, field
from typing import Any

_counter = itertools.count()


@dataclass(order=True)
class PriorityTask:
    """Lower urgency number = higher priority (0=critical, 9=low)

    FIX: A monotonic sequence number is used as a tie-breaker so that
    payloads of any type (dict, list, etc.) are never compared.
    The message field is excluded from comparison entirely.
    """
    urgency: int
    seq: int = field(default_factory=lambda: next(_counter))
    message: Any = field(compare=False)
