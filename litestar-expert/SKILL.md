---
name: litestar-expert
description: Expert-level guidance for building web applications with Litestar framework. Use when working with Litestar for creating ASGI web applications, REST APIs, WebSocket endpoints, dependency injection, DTOs, middleware, routing, authentication/authorization, OpenAPI documentation, or any Litestar-specific development tasks. Covers route handlers, controllers, routers, request/response handling, layered architecture, and advanced features like channels, caching, and background tasks.
---

# Litestar Expert

Use Litestar to build ASGI APIs with clean routing, DTOs, DI, middleware, security, and OpenAPI.

## Quick Workflow

1. Pick handler style: functions for small services, controllers for larger modules.
2. Set shared config at the right layer (app/router/controller/handler).
3. Define DTOs for inputs and outputs before wiring handlers.
4. Wire dependencies with `Provide` (use yield deps for cleanup).
5. Add middleware and guards for cross-cutting concerns.
6. Configure OpenAPI only after routes stabilize.
7. Test endpoints with `TestClient`.

## Decision Guide

- Function handler vs controller: small surface vs grouped resources.
- DTO choice: `PydanticDTO` for Pydantic models, `DataclassDTO` for dataclasses, `MsgspecDTO` for msgspec.Struct.
- WebSocket listener vs handler: listeners for simple IO, handlers for full control.
- Security: guards for policy checks, JWT middleware for auth, session middleware for browser flows.
- OpenAPI: defaults for small APIs, custom config for production docs.

## Non-Negotiables

- Layered config precedence: handler overrides controller, overrides router, overrides app.
- Do not return ORM entities directly; use `return_dto`.
- Keep auth and policy out of handlers; use guards and middleware.

## Minimal Skeleton

```python
from litestar import Litestar, Router, Controller, get
from litestar.di import Provide

async def get_db() -> Database:
    return Database()

class HealthController(Controller):
    path = "/health"

    @get()
    async def status(self) -> dict:
        return {"ok": True}

api = Router(path="/api", route_handlers=[HealthController])

app = Litestar(
    route_handlers=[api],
    dependencies={"db": Provide(get_db)},
)
```

## Read These References When Needed

- Routing rules, path params, and router options: `references/routing.md`
- DTO config and partial updates: `references/dto.md`
- Dependency injection patterns: `references/dependencies.md`
- Request parsing and uploads: `references/requests.md`
- Response types and pagination: `references/responses.md`
- Middleware composition and ordering: `references/middleware.md`
- Auth, guards, and JWT: `references/security.md`
- WebSockets and streaming: `references/websockets.md`
- OpenAPI customization: `references/openapi.md`
