"""Public interface for the event_bus package.

This module exposes the key types and classes for external use:
- Handler and AsyncHandler: typing aliases for sync and async event handlers.
- Subscription: token object representing a handler’s registration.
- EventBus: synchronous publish/subscribe event bus.
- AsyncEventBus: asyncio-based publish/subscribe event bus.

By defining `__all__`, only these names are exported when using
`from event_bus import *`, providing a clean public API surface.
"""

from .types import Handler, AsyncHandler, Subscription
from .sync_bus import EventBus
from .async_bus import AsyncEventBus

__all__ = [
    "Handler",
    "AsyncHandler",
    "Subscription",
    "EventBus",
    "AsyncEventBus",
]
