# Hexagonal Architecture

## Core Concepts

- Domain core contains business logic.
- Ports define the core's needs and capabilities.
- Adapters implement ports for external systems.

## Ports and Adapters

```
Domain Core <-> Ports <-> Adapters <-> External Systems
```

## When to Use

- You need strong testability with mockable adapters.
- You want to swap infrastructure without changing the core.
- You prefer interaction-based boundaries over layered packages.

## Minimal Example

```python
class PaymentGatewayPort:
    async def charge(self, amount, customer):
        raise NotImplementedError

class StripePaymentAdapter(PaymentGatewayPort):
    async def charge(self, amount, customer):
        return {"success": True}
```
