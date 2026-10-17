# Modular Monolith Layout and Wiring

## Recommended Project Layout

```
src/
  app/
    main.py                 # composition root
    settings.py             # config (pydantic-settings)
    infra/
      db.py                 # engine/session factory
      logging.py
      events.py             # event bus abstraction + implementation
    modules/
      users/
        api.py              # APIRouter (HTTP layer)
        public.py           # module public API (facade/use-cases)
        domain.py           # entities/value objects (optional)
        application.py      # use-cases (optional)
        repo.py             # persistence adapters
        schemas.py          # DTOs (Pydantic)
        wiring.py           # module-local wiring helpers
        __init__.py
      billing/
        api.py
        public.py
        ...
      inventory/
        api.py
        public.py
        ...
  tests/
    integration/
    contract/
```

Guideline: `modules/<name>/public.py` is the only file other modules may import.

## Composition Root (Minimal)

```python
from fastapi import FastAPI
from app.infra.db import init_db
from app.modules.users.api import router as users_router
from app.modules.billing.api import router as billing_router

def create_app() -> FastAPI:
    app = FastAPI()
    init_db(app)

    app.include_router(users_router, prefix="/users", tags=["users"])
    app.include_router(billing_router, prefix="/billing", tags=["billing"])
    return app

app = create_app()
```

## Wiring Rule

Keep module wiring close to the module or composition root. Do not scatter dependency wiring across modules or infra.
