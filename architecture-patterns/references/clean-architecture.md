# Clean Architecture

## Layers (Dependency Flows Inward)

- Entities: core business models and rules
- Use cases: application orchestration
- Interface adapters: controllers, presenters, gateways
- Frameworks and drivers: UI, database, external services

## Key Principles

- Inner layers know nothing about outer layers.
- Business logic is framework-agnostic.
- Tests should run without UI, DB, or external services.

## Directory Layout (Example)

```
app/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   └── interfaces/
├── use_cases/
├── adapters/
│   ├── repositories/
│   ├── controllers/
│   └── gateways/
└── infrastructure/
```

## Minimal Example

```python
# use_cases/create_user.py
class CreateUserUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def execute(self, request):
        existing = await self.user_repository.find_by_email(request.email)
        if existing:
            return {"success": False, "error": "Email exists"}
        user = await self.user_repository.save(request)
        return {"success": True, "user": user}
```
