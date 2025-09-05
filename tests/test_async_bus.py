"""
Tests for the `AsyncEventBus` class.

This module contains unit tests for the `AsyncEventBus` class, which provides
asynchronous event-driven communication. The tests ensure that the class
functions correctly in various scenarios, including subscribing, publishing,
unsubscribing, clearing subscribers, and handling invalid inputs.

Tested functionality includes:
- Asynchronous subscription and publishing of events.
- Correct invocation of subscribed handlers with the appropriate event
    and payload.
- Unsubscribing handlers and verifying the updated subscriber count.
- Clearing all subscribers from the event bus.
- Handling invalid inputs for subscription and publishing.

The tests use the `pytest` framework with the `pytest-asyncio` plugin for
asynchronous test execution.
"""
import asyncio
import pytest
from event_bus import AsyncEventBus

pytestmark = pytest.mark.asyncio


async def test_async_subscribe_publish_unsubscribe():
    """
    Test the asynchronous subscribe, publish, and unsubscribe
        functionality of the AsyncEventBus.

    This test verifies the following:
    1. Subscribing multiple asynchronous handlers to an event and ensuring
        the correct count of subscribers.
    2. Publishing an event and confirming that all subscribed handlers are
        invoked with the correct event and payload.
    3. Unsubscribing a handler and ensuring the count of subscribers is
        updated correctly.
    4. Publishing the event again and verifying that only the remaining
        subscribed handlers are invoked.
    5. Unsubscribing all handlers and ensuring no handlers remain subscribed.

    The test uses two asynchronous handlers (`ah1` and `ah2`) to simulate
        event handling.
    """
    bus = AsyncEventBus()

    seen = []

    async def ah1(event, payload):
        await asyncio.sleep(0)
        seen.append((event, payload))

    async def ah2(event, payload):
        seen.append((event, payload))

    s1 = bus.subscribe("user.logged_in", ah1)
    s2 = bus.subscribe("user.logged_in", ah2)
    assert bus.count_subscribers("user.logged_in") == 2

    fired = await bus.publish("user.logged_in", {"user_id": 42})
    assert fired == 2
    assert seen == [
        ("user.logged_in", {"user_id": 42}),
        ("user.logged_in", {"user_id": 42})
        ]

    bus.unsubscribe(s1)
    assert bus.count_subscribers("user.logged_in") == 1

    fired = await bus.publish("user.logged_in", {"user_id": 43})
    assert fired == 1

    bus.unsubscribe(s2)


@pytest.mark.asyncio
def test_clear():
    """
    Test the `clear` method of the `AsyncEventBus` class.

    This test ensures that the `clear` method removes all
        subscribers from the event bus.
    It performs the following steps:
    1. Creates an instance of `AsyncEventBus`.
    2. Defines an asynchronous dummy subscriber function.
    3. Subscribes the dummy function to an event named "e".
    4. Asserts that the number of subscribers for the event "e" is 1.
    5. Calls the `clear` method to remove all subscribers.
    6. Asserts that the number of subscribers for the event "e" is now 0.
    """
    bus = AsyncEventBus()

    async def dummy(_event, _payload):
        return None

    bus.subscribe("e", dummy)
    assert bus.count_subscribers("e") == 1
    bus.clear()
    assert bus.count_subscribers("e") == 0


async def test_invalid_inputs_async():
    """
    Test the `AsyncEventBus` for handling invalid inputs.

    This test ensures that the `AsyncEventBus` raises appropriate exceptions
    when provided with invalid arguments for subscription and publishing.

    - Verifies that subscribing with an invalid event name
        (e.g., an empty string)
        raises an `AssertionError`.
    - Verifies that publishing an event with an invalid event
        type (e.g., a non-string)
        raises an `AssertionError`.
    """
    bus = AsyncEventBus()
    with pytest.raises(AssertionError):
        bus.subscribe("", lambda e, p: None)  # type: ignore[arg-type]
    with pytest.raises(AssertionError):
        await bus.publish(123)  # type: ignore[arg-type]
