---
name: pydantic-models-py
description: Create Pydantic models following the multi-model pattern with Base, Create, Update, Response, and InDB variants. Use when defining API request/response schemas, database models, or data validation in Python applications using Pydantic v2.
---

# Pydantic Models

Create Pydantic v2 models using a multi-model pattern for clean API contracts.

## Quick Workflow

1. Define a `Base` model with shared fields.
2. Create `Create` (required inputs) and `Update` (all optional) variants.
3. Add `Response` for output shape.
4. Only add persistence-specific fields in a separate model when necessary.

## Boundary Rules (Align with boundary-validation)

- Treat Pydantic models as **Layer 1 DTOs** only.
- Allowed: type coercion, bounds, formats, small invariants (`start < end`).
- Forbidden: business policy, database lookups, or calls to services.

## Multi-Model Pattern

| Model | Purpose |
|-------|---------|
| `Base` | Common fields shared across models |
| `Create` | Request body for creation (required fields) |
| `Update` | Request body for updates (all optional) |
| `Response` | API response with all fields |
| `Persistence` | Storage-specific fields (only if needed) |

## Minimal Example

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

class ProjectCreate(ProjectBase):
    owner_id: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
```

## Aliases (camelCase)

```python
class MyModel(BaseModel):
    workspace_id: str = Field(..., alias="workspaceId")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}
```

## Optional Update Fields

```python
class MyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
```

## Persistence Model (Optional)

```python
class ProjectPersistence(ProjectResponse):
    doc_type: str = "project"
```
