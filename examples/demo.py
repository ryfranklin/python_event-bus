"""Example usage of the synchronous EventBus.

This script demonstrates how to:
- Define simple event handler functions.
- Subscribe handlers to an event.
- Publish events to invoke handlers.
- Observe the printed output in the console.
"""
from event_bus import EventBus


def log_handler(event: str, payload):
    """
    Example handler that logs the event and its payload.

    Args:
        event (str): The name of the event being published.
        payload (Any): Arbitrary data associated with the event.
    """
    print(f"[LOG] {event}: {payload}")


def count_handler(event: str):
    """
    Example handler that reports the event occurrence.

    Args:
        event (str): The name of the event being published.
    """
    print(f"Count handler saw {event}")


if __name__ == "__main__":
    bus = EventBus()

    sub1 = bus.subscribe("order.created", log_handler)
    sub2 = bus.subscribe("order.created", count_handler)

    fired = bus.publish("order.created", {"id": 123, "amount": 45.0})
    print("fired:", fired)

    bus.unsubscribe(sub1)
    fired = bus.publish("order.created", {"id": 456})
    print("fired after unsubscribe:", fired)

    bus.clear()
