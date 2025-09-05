from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Awaitable

# Public typing aliases
Handler = Callable[[str, Any], None]
AsyncHandler = Callable[[str, Any], Awaitable[None]]


@dataclass(frozen=True)
class Subscription:
    """Represents a (event_name, handler) pair.

    Attributes
    ----------
    event : str
        The name/topic of the event.
    handler : Handler | AsyncHandler
        The callable to invoke when the event is published.
    """

    event: str
    handler: Callable[..., Any]
