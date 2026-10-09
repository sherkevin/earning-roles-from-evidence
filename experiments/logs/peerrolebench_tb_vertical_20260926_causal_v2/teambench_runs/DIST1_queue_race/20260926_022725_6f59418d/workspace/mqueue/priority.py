"""Priority-ordered task message wrapper."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PriorityTask:
    """Order tasks by urgency and a numeric sequence tie-breaker."""

    urgency: int
    seq: int
    message: Any = field(compare=False)
