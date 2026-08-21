# Domain-Driven Design (DDD)

## Strategic Patterns

- Bounded contexts define clear domain boundaries.
- Context maps describe relationships between contexts.
- Ubiquitous language keeps model and conversation aligned.

## Tactical Patterns

- Entities: identity and lifecycle
- Value objects: immutable, validated at construction
- Aggregates: consistency boundaries
- Repositories: persistence abstraction
- Domain events: record business facts

## Minimal Example

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

class Order:
    def __init__(self, order_id: str):
        self.id = order_id
        self.items = []

    def add_item(self, item):
        self.items.append(item)
```
