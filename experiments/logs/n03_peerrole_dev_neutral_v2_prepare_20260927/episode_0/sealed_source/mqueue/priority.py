
from dataclasses import dataclass, field
from typing import Any
import itertools

_counter = itertools.count()


@dataclass(order=True)
class PriorityTask:
    urgency: int
    _seq: int = field(default_factory=lambda: next(_counter), compare=True, repr=False)
    message: Any = field(compare=False)
