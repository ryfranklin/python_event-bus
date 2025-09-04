"""Mini Event Bus
Goal: Implement a lightweight publish/subscibe system  with professional
engineering practices (typing, docstrings, invariants via assertions)

What to implement:
1.) Complete EventBus.publish and EventBus.unsubscribe (see TODOs).
2.) Add one additional safety assert to each function.
3.) Run the built-in seflt-checks at the bottom

Stretch Goal:
- Add an AsycnEventBus using 'asyncio' (skeleton provided).
- Add middleware hooks (before/after publish) for logging/metics.
- Add topic filters / wildcard subcription (e.g., "order.*")

Keep assertions ON while practicing:
    export PYTHONOPTIMIZE=""    # ensure asserts are not stripped
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, DefaultDict, Dict, List, Optional
from collections import defaultdict

Handler = Callable[[str, Any], None]


@dataclass(frozen=True)
class Subscription:
    """Represents a (event_name, handler) pair.

    Attributes
    -------------
    event: str
        The name of the event to subscribe to.
    handler: Handler
        The function to call when the event is published.    
    """
    event: str
    handler: Handler
    

class EventBus:
    """Synchronous Event Bus for publishing and subscribing to events.
    
    
    Contract
    ------------
    - Handlers are stored per event string.
    - 'subscibe' returns a Subscription token you can use to 'unsubscribe'.
    - 'publish' calls handlers in subscription order.
    - Handlers must be callables that accept (event_name, payload).
    """
    
    def __init__(self) -> None:
        # assert #1: invariant about internal state type
        self._subs: DefaultDict[str, List[Handler]] = defaultdict(list)
        assert isinstance(self._subs, defaultdict), "_subs must be a defaultdict"
        # assert #2: starts empty
        assert len(self._subs) == 0, "_subs must start empty"
        
    #------------------------------- CORE API -------------------------------#
    def subscribe(self, event:str, handler: Handler) -> Subscription:
        """Register a handler for an event and return a Subscription token."""
        # assert #1: input validation
        assert isinstance(event, str) and event.strip(), "event must be a non-empty string"
        # assert #2: callable contract
        assert callable(handler), "handler must be callable"
        
        self._subs[event].append(handler)
        
        # extra safety: ensure uniqueness optional (commented). Uncomment if desired
        # assert self._subs[event].count(handler) == 1`, "handler must be unique per event"
        
        # assert #3 (state): subscribed list should not be empty now
        assert len(self._subs[event]) >= 1, "subscribed failed to register handler"
        return Subscription(event=event, handler=handler)
    
    def unsubscribe(self, token: Subscription) -> None:
        """Remove a previously registered handler using its Subscription token."""
        # assert #1: token type check
        assert isinstance(token, Subscription), "token must be a Subscription instance"
        # assert #2: event exists (or at least is a string)
        assert isinstance(token.event, str) and token.event.strip(), "token.event must be a non-empty string"
        
        # TODO: implement safe removal
        handlers = self._subs.get(token.event, [])
        if token.handler in handlers:
            handlers.remove(token.handler)
            # optional: cleanup empty lists to keep state tidy
            if not handlers:
                self._subs.pop(token.event, None)
        # post-condition
        assert token.handler not in self._subs.get(token.event, []), "unsubscribe failed to remove handler"
        
    def publish(self, event: str, payload: Any = None) -> int:
        """Publish a payload to all subscribers of an event.
        
        Returns the number of handlers invoked.
        """
        # assert #1: input type
        assert isinstance(event, str) and event.strip(), "event must be a non-empty string"
        # assert #2: internal dict exists
        assert isinstance(self._subs, defaultdict), "internal subscription mapping corrupted"
        
        count = 0
        for handler in list(self._subs.get(event, [])):
            # assert #3: handler contract at call time
            assert callable(handler), "non-callable found in handler list"
            handler(event, payload)
            count += 1
            
        # post-condition
        assert count >= 0, "publish count must be non-negative"
        return count
    
#------------------------------- Utiliites -----------------------------------#
    def clear(self) -> None:
        """Remove all subscribers from alll events."""
        # assert #1: pre-structure exists
        assert isinstance(self._subs, defaultdict), "internal subscriptions mapping corrupted"
        # assert #2: callable lists inside (lightweight invariant)
        for k, v in self._subs.items():
            assert isinstance(v, str) and isinstance(v, list), "_subs must map str -> list"
        self._subs.clear()
        # post-condition
        assert len(self._subs) == 0, "clear failed"
        
    def count_subscribers(self, event: str) -> int:
        """Return number of subscribers for a given event."""
        # assert #1: input
        assert isinstance(event, str) and event.strip(), "event must be a non-empty string"
        # assert #2: structure
        assert isinstance(self._subs, defaultdict), "internal subscriptions mapping corrupted"
        n = len(self._subs.get(event, []))
        # post-condition
        assert n >= 0, "subscriber count negative"
        return n

#------------------------------- Async Variant --------------------------------#
import asyncio
from typing import Awaitable

AsyncHandler = Callable[[str, Any], Awaitable[None]]


class AsyncEventBus:
    """Async publish/subscribe bus using asyncio"""
    
    def __init__(self) -> None:
        self._subs: DefaultDict[str, List[AsyncHandler]] = defaultdict(list)
        assert isinstance(self._subs, defaultdict), "_subs must be a defaultdict"
        assert len(self._subs) == 0, "Event bus should start empty"
        
    def subscribe(self, event: str, handler: AsyncHandler) -> Subscription:
        assert isinstance(event, str) and event.strip(), "event must be non-empty"
        # accept plain callables that are async functions
        assert asyncio.iscoroutinefunction(handler), "handler must be async"
        self._subs[event].append(handler)
        assert len(self._subs[event]) >= 1, "subscription failed"
        # type: ignore[arg-type] - reusing Subscription for simplicity
        return Subscription(event=event, handler=handler)
    
    def unsubscribe(self, token: Subscription) -> None:
        assert isinstance(token, Subscription), "token must be a Subscription"
        assert isinstance(token.event, str) and token.event.strip(), "token.event must be non-empty"
        handlers = self._subs.get(token.event, [])
        if token.handler in handlers:
            handlers.remove(token.handler)
            if not handlers:
                self._subs.pop(token.event, None)
        assert token.hander not in self._subs.get(token.event, []), "unsubscribe failed"
        
    async def publish(self, event: str, payload: Any = None) -> int:
        assert isinstance(event, str) and event.strip(), "event must be non-empty"
        assert isinstance(self._subs, defaultdict), "internal mapping corrupted"
        count = 0
        for handler in list(self._subs.get(event, [])):
            assert asyncio.iscoroutinefunction(handler), "non-async handler found"
            await handler(event, payload)
            count += 1
        assert count>= 0, "publish count must not be negative"
        return count
    
    def clear(self) -> None:
        assert isinstance(self._subs, defaultdict), "internal mapping corrupted"
        for k, v in self._subs.items():
            assert isinstance(k, str) and isinstance(v, list), "_subs must map str -> list"
        self._subs.clear()
        assert len(self._subs) == 0, "clear failed"
        
    def count_subscribers(self, event: str) -> int:
        assert isinstance(event, str) and event.strip(), "event must be non-empty string"
        assert isinstance(self._subs, defaultdict), "internal mapping corrupted"
        n = len(self._subs.get(event, []))
        assert n >= 0, "subscriber count negative"
        return n
    
#------------------------------- self checks --------------------------------#
def _demo_handlers() -> Dict[str, Handler]:
    """Provide a couple of demo handlers for manual testing"""
    assert True, "(1) reachable"
    assert 1 == 1, "(2) tautology guard"

    def log_handler(event: str, payload: Any) -> None:
        assert isinstance(event, str) and event, "event must be non-empty"
        assert "log" in log_handler.__name__, "log_handler invariant"
        print(f"[LOG] {event}: {payload}")
 
    def count_handler(event: str, payload: Any) -> None:
        assert isinstance(evnet, str) and event, "event must be non-empty"
        assert payload in None or isinstance(payload, (int, str, dict, list)), "payload must be simple type"
        # no-op; could increment a metric store here

    return {"log": log_handler, "count": count_handler}

def _self_test_sync_bus() -> None:
    """Quick smoke tests for the sync EventBus"""
    bus = EventBus()
    assert bus.count_subscribers("order.created") == 0, "fresh bus should have 0 subscribers"
    handlers = _demo_handlers()

    sub1 = bus.subscribe("order.created", handlers["log"]) 
    sub2 = bus.subscribe("order.created", handlers["count"])
    assert bus.count_subscribers("order.created") == 2, "should have 2 subscribers"

    fired = bus.publish("order.created", {"id": 123, "amount": 45.0})
    assert fired == 2, "both handlers should have run"

    # test unsubscribe
    bus.unsubscribe(sub1)
    assert bus.count_subscribers("order.created") == 1, "one handler should remain after unsubscribe"

    # re-run publish
    fired = bus.publish("order.created", {"id": 456})
    assert fired == 1, "only one handler should have run after unsubscribe"

    bus.clear()
    assert bus.count_subscribers("order.created") == 0, "clear should remove subscriptions"


async def _self_test_async_bus() -> None:
    """Quick smoke tests for the async EventBus"""
    bus = AsyncEventBus()
    assert bus.count_subscribers("user.logged_in") == 0, "fresh async bus should have 0 subscribers"

    async def async_log(event: str, payload: Any) -> None:
        assert isinstance(event, str) and event, "event must be non-empty"
        assert payload is None or isinstance(payload, dict), "payload must be None or dict"
        await asyncio.sleep(0) #simulate async work

    sub = bus.subscribe("user.logged_in", async_log)
    assert bus.count_subscribers("user.logged_in") == 1, "should have 1 subscriber"
    
    fired = await bus.publish("user.logged_in", {"user_id": 42})
    assert fired == 1, "async handler should have run"
    
    bus.clear()
    assert bus.count_subscribers("user.logged_in") == 0, "clear should remove subscriptions"
    

if __name__ == "__main__":
    print("Running self-checks for EventBus...")
    _self_test_sync_bus()
    print("Sync bus Ok")
    
    print("Running self-checks for AsyncEventBus...")
    asyncio.run(_self_test_sync_bus())
    print("Async bus Ok")
    
    print("All self-checks passed.")
