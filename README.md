# Mini Event Bus

A lightweight publish/subscribe system built in Python, with both synchronous and asynchronous variants.

Practicing the Observer Pattern and writing production-ready code with:
	•	🧩 Decoupling via publish/subscribe
	•	🛡️ Assertions to enforce invariants
	•	🧪 Pytest suites for sync & async buses
	•	📖 Docstrings and clear module documentation
	•	🏗️ Refactor into a package (event_bus/) with examples
 ___

📚 What is an Event Bus?

An Event Bus is a design pattern that lets components communicate without tight coupling:
	•	Publishers emit events (order.created, user.logged_in).
	•	Subscribers register handlers to react to those events.
	•	The Event Bus routes payloads from publishers to subscribers.

This is the same concept used in frameworks and systems like Django signals, Node.js EventEmitter, and enterprise message brokers (Kafka, RabbitMQ).
___

### ✨ Features
    - Sync Bus (EventBus)
    - Register (subscribe) and unregister (unsubscribe) handlers
    - Broadcast events with payloads to all subscribers (publish)
    - Manage state with clear() and count_subscribers()
    - Async Bus (AsyncEventBus)
    - Async/await handlers supported
    - Runs on asyncio event loop
    - Safety via Assertions
    - Every function includes ≥ 2 assert statements for input validation and invariants
    - Catches bad states early (defensive programming)
    - Testing
    - Pytest suites for both sync and async
    - Covers valid flows and invalid inputs
    - Examples
    - examples/demo.py shows how to wire handlers and publish events
___

### 🛠️ Installation

Clone the repo and install in editable mode:
___
``` bash
git clone https://github.com/<your-username>/python-event-bus.git
cd python-event-bus
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
pip install pytest pytest-asyncio
```
___
### Synchronous Example
``` python
from event_bus import EventBus

def log_handler(event, payload):
    print(f"[LOG] {event}: {payload}")

def count_handler(event, payload):
    print(f"Count handler saw {event}")

bus = EventBus()

# Subscribe handlers
sub1 = bus.subscribe("order.created", log_handler)
sub2 = bus.subscribe("order.created", count_handler)

# Publish event
bus.publish("order.created", {"id": 123, "amount": 45.0})

# Unsubscribe one handler
bus.unsubscribe(sub1)

# Clear all
bus.clear()
```
___

### Running Tests
pytest
- tests/test_sync_bus.py -> tests synchronous bus
- tests/test_async_bus.py -> tests async bus (required pytest-asyncio)
