# Pipeline Orchestration

## Standard Stage Flow

```
Build → Test → Staging → Approve → Production → Verify → Rollback
```

## Stage Responsibilities

- Build: compile/package, create artifacts
- Test: unit/integration/security checks
- Staging: deploy and validate integration
- Approve: manual or timed approval
- Production: controlled rollout
- Verify: health checks, SLO signals
- Rollback: automated fallback
