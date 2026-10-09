from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PriorityTask:
    """Order messages without comparing arbitrary payloads."""

    urgency: int
    seq: int
    message: Any = field(compare=False)
