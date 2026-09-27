
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PriorityTask:
    urgency: int
    sequence: int = field(compare=True, default=0)
    message: Any = field(compare=False, default=None)
