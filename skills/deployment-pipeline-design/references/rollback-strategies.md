# Rollback Strategies

## Automated Rollback

- Trigger on failed health checks or error rate thresholds.
- Use `kubectl rollout undo` or equivalent for your platform.

## Manual Rollback

- Keep runbooks and revision history.
- Prefer one-command rollback paths.
