"""Unit tests for the synchronous EventBus.

This test suite ensures that:
- Handlers can be subscribed, invoked through publish,
    and unsubscribed correctly.
- The `clear()` method removes all registered subscriptions.
- Invalid inputs to `subscribe` and `publish` raise appropriate
    AssertionErrors.

The tests are written with pytest and act as executable specifications
for the expected behavior of the EventBus.
"""

import pytest
from event_bus import EventBus


def test_subscribe_publish_unsubscribe():
    """Verify that subscribing multiple handlers works, publishing delivers
    payloads to all of them, and unsubscribing removes the handler.

    Steps:
    - Subscribe two handlers to the same event.
    - Confirm both are invoked when the event is published.
    - Unsubscribe one handler and confirm only the other runs on publish.
    """
    bus = EventBus()
    seen = []

    def h1(event, payload):
        seen.append((event, payload))

    def h2(event, payload):
        seen.append((event, payload))

    s1 = bus.subscribe("order.created", h1)
    s2 = bus.subscribe("order.created", h2)
    assert bus.count_subscribers("order.created") == 2

    fired = bus.publish("order.created", {"id": 1})
    assert fired == 2
    assert seen == [("order.created", {"id": 1}), ("order.created", {"id": 1})]

    bus.unsubscribe(s1)
    assert bus.count_subscribers("order.created") == 1

    fired = bus.publish("order.created", {"id": 2})
    assert fired == 1

    bus.unsubscribe(s2)
    assert bus.count_subscribers("order.created") == 0


def test_clear():
    """
    Verify that calling `clear()` removes all event subscriptions.

    Steps:
    - Subscribe a handler to an event.
    - Confirm count is 1.
    - Call `clear()` and confirm subscriber count drops to 0.
    """
    bus = EventBus()
    bus.subscribe("e", lambda e, p: None)
    assert bus.count_subscribers("e") == 1
    bus.clear()
    assert bus.count_subscribers("e") == 0


def test_invalid_inputs():
    """
    Verify that invalid inputs to `subscribe` and `publish`
    raise AssertionError.

    Cases:
    - Subscribing with an empty event name should raise.
    - Publishing with a non-string event name should raise.
    """
    bus = EventBus()
    with pytest.raises(AssertionError):
        bus.subscribe("", lambda e, p: None)
    with pytest.raises(AssertionError):
        bus.publish(123)  # type: ignore[arg-type]
