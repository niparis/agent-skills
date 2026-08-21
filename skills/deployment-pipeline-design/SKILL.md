---
name: deployment-pipeline-design
description: Design multi-stage CI/CD pipelines with approval gates, security checks, and deployment orchestration. Use when architecting deployment workflows, setting up continuous delivery, or implementing GitOps practices.
---

# Deployment Pipeline Design

Design multi-stage CI/CD pipelines that balance speed, safety, and observability.

## Quick Workflow

1. Map environments and promotion rules.
2. Define stages: build, test, deploy, verify, rollback.
3. Decide approval and gating strategy.
4. Choose deployment strategy per service.
5. Add automated verification and rollback.

## Decision Guide

- Approval gates: use for production or high-risk changes.
- Canary vs blue-green: canary for gradual risk reduction, blue-green for instant cutover.
- Feature flags: use when rollout should be decoupled from deployment.
- GitOps: use when you need auditability and clear drift detection.

## Non-Negotiables

- Promote artifacts, not source code.
- Separate deploy and verify; never skip verification.
- Define rollback triggers up front.

## Read These References When Needed

- Stage breakdown and orchestration: `references/pipeline-orchestration.md`
- Approval gate patterns: `references/approval-gates.md`
- Deployment strategies: `references/deployment-strategies.md`
- Rollback patterns: `references/rollback-strategies.md`
- Monitoring and metrics: `references/monitoring-metrics.md`
