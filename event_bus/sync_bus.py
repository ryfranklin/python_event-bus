from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, List, Any

from .types import Handler, Subscription


class EventBus:
    """Synchronous in-process publish/subscribe bus.

    Contract
    --------
    - Handlers are stored per event string.
    - `subscribe` returns a Subscription token you can use to `unsubscribe`.
    - `publish` calls handlers in subscription order.
    - Handlers must be callables that accept (event_name: str, payload: Any).
    """

    def __init__(self) -> None:
        self._subs: DefaultDict[str, List[Handler]] = defaultdict(list)
        # Invariants
        assert isinstance(self._subs, defaultdict), \
            "_subs must be a defaultdict"
        assert len(self._subs) == 0, "Event bus should start empty"

    # -------------------- core API --------------------
    def subscribe(self, event: str, handler: Handler) -> Subscription:
        """Register a handler for an event and return a Subscription token.

        Args:
            event: Event name/topic to subscribe to (non-empty).
            handler: Callable invoked as handler(event_name, payload).

        Returns:
            Subscription token used to later `unsubscribe` the handler.
        """
        assert isinstance(event, str) and event.strip(), \
            "event must be a non-empty string"
        assert callable(handler), "handler must be callable"

        self._subs[event].append(handler)
        # Optional uniqueness check:
        # assert self._subs[event].count(handler) == 1, "duplicate
        # handler subscription detected"

        assert len(self._subs[event]) >= 1, \
            "subscription failed to register handler"
        return Subscription(event=event, handler=handler)

    def unsubscribe(self, token: Subscription) -> None:
        """Remove a previously registered handler using its Subscription token.

        Args:
            token: Subscription returned by `subscribe`.
        """
        assert isinstance(token, Subscription), \
            "token must be a Subscription instance"
        assert isinstance(token.event, str) and token.event.strip(), (
            "token.event must be a non-empty string"
        )

        handlers = self._subs.get(token.event, [])
        if token.handler in handlers:
            handlers.remove(token.handler)
            if not handlers:
                # Keep mapping tidy when no handlers remain
                self._subs.pop(token.event, None)

        # Post-condition: handler no longer present
        assert token.handler not in self._subs.get(token.event, []), (
            "unsubscribe failed to remove handler"
        )

    def publish(self, event: str, payload: Any = None) -> int:
        """Publish a payload to all subscribers of an event.

        Args:
            event: Name/topic to publish (non-empty).
            payload: Arbitrary data delivered to handlers.

        Returns:
            Number of handlers invoked.
        """
        assert isinstance(event, str) and event.strip(), \
            "event must be a non-empty string"
        assert isinstance(self._subs, defaultdict), \
            "internal subscriptions mapping corrupted"

        count = 0
        for handler in list(self._subs.get(event, [])):
            assert callable(handler), "non-callable found in handler list"
            handler(event, payload)
            count += 1

        assert count >= 0, "publish count must be non-negative"
        return count

    # -------------------- utilities --------------------
    def clear(self) -> None:
        """Remove all subscribers from all events."""
        assert isinstance(self._subs, defaultdict), \
            "internal subscriptions mapping corrupted"
        for k, v in self._subs.items():
            assert isinstance(k, str) and isinstance(v, list), \
                "_subs must map str -> list"
        self._subs.clear()
        assert len(self._subs) == 0, "clear failed"

    def count_subscribers(self, event: str) -> int:
        """Return number of subscribers for a given event."""
        assert isinstance(event, str) and event.strip(), \
            "event must be a non-empty string"
        assert isinstance(self._subs, defaultdict), \
            "internal subscriptions mapping corrupted"
        n = len(self._subs.get(event, []))
        assert n >= 0, "subscriber count negative"
        return n
