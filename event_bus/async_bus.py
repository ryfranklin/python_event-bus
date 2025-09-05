"""Unit tests for the synchronous EventBus implementation.

These tests cover:
- Subscribing, publishing, and unsubscribing handlers.
- Clearing all subscribers with `clear()`.
- Handling of invalid inputs that should raise AssertionError.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, DefaultDict, List

from .types import AsyncHandler, Subscription


class AsyncEventBus:
    """Async publish/subscribe bus using asyncio.

    Handlers must be *async* callables with signature `(
        event_name: str,
        payload: Any
        )`.
    """

    def __init__(self) -> None:
        self._subs: DefaultDict[str, List[AsyncHandler]] = defaultdict(list)
        assert isinstance(self._subs, defaultdict), \
            "_subs must be a defaultdict"
        assert len(self._subs) == 0, "Event bus should start empty"

    def subscribe(self, event: str, handler: AsyncHandler) -> Subscription:
        """Register an asynchronous handler for an event.

        Args:
            event: Event name/topic to subscribe to (non-empty).
            handler: Async function `async def handler(
                event: str,
                payload: Any
                ) -> None`.

        Returns:
            Subscription token for later unsubscription.
        """
        assert isinstance(event, str) and event.strip(), \
            "event must be non-empty"
        assert asyncio.iscoroutinefunction(handler), "handler must be async"

        self._subs[event].append(handler)
        assert len(self._subs[event]) >= 1, "subscription failed"
        # Reuse Subscription for simplicity
        return Subscription(event=event, handler=handler)

    def unsubscribe(self, token: Subscription) -> None:
        """
        Remove a previously registered async handler using its
        Subscription token.
        Args:
            token: Subscription returned by `subscribe`.
        """
        assert isinstance(token, Subscription), "token must be a Subscription"
        assert isinstance(token.event, str) and token.event.strip(), \
            "token.event must be non-empty"

        handlers = self._subs.get(token.event, [])
        if token.handler in handlers:
            handlers.remove(token.handler)  # type: ignore[arg-type]
            if not handlers:
                self._subs.pop(token.event, None)

        assert token.handler not in self._subs.get(token.event, []), \
            "unsubscribe failed"

    async def publish(self, event: str, payload: Any = None) -> int:
        """Publish an event to all async handlers and await each in order.

        Args:
            event: Event name/topic to publish (non-empty).
            payload: Arbitrary data delivered to handlers.

        Returns:
            Number of handlers awaited.
        """
        assert isinstance(event, str) and event.strip(), \
            "event must be non-empty"
        assert isinstance(self._subs, defaultdict), \
            "internal mapping corrupted"

        count = 0
        for handler in list(self._subs.get(event, [])):
            assert asyncio.iscoroutinefunction(handler), \
                "non-async handler found"
            await handler(event, payload)
            count += 1

        assert count >= 0, "publish count must not be negative"
        return count

    def clear(self) -> None:
        """Remove all event subscriptions from the async bus."""
        assert isinstance(self._subs, defaultdict), \
            "internal mapping corrupted"
        for k, v in self._subs.items():
            assert isinstance(k, str) and isinstance(v, list), \
                "_subs must map str -> list"
        self._subs.clear()
        assert len(self._subs) == 0, "clear failed"

    def count_subscribers(self, event: str) -> int:
        """Return number of async subscribers for a given event."""
        assert isinstance(event, str) and event.strip(), \
            "event must be a non-empty string"
        assert isinstance(self._subs, defaultdict), \
            "internal mapping corrupted"
        n = len(self._subs.get(event, []))
        assert n >= 0, "subscriber count negative"
        return n
