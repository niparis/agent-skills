# Approval Gates

## Manual Approval (GitHub Actions)

```yaml
environment:
  name: production
  url: https://app.example.com
```

## Time-Based Approval (GitLab)

```yaml
when: delayed
start_in: 30 minutes
```

## Multi-Approver (Azure Pipelines)

```yaml
- task: ManualValidation@0
  inputs:
    notifyUsers: "team-leads@example.com"
    instructions: "Review staging metrics before approving"
```
