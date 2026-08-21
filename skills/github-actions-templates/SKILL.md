---
name: github-actions-templates
description: Create production-ready GitHub Actions workflows for automated testing, building, and deploying applications. Use when setting up CI/CD with GitHub Actions, automating development workflows, or creating reusable workflow templates.
---

# GitHub Actions Templates

Use this skill to design GitHub Actions workflows that are secure, fast, and easy to maintain.

## Quick Workflow

1. Identify triggers (push, pull_request, schedule, workflow_call).
2. Define jobs with least-privilege permissions.
3. Add caching and concurrency controls.
4. Choose reusable workflows for shared patterns.
5. Add deployment gates using environments.

## Decision Guide

- Matrix builds: use for multi-version testing.
- Reusable workflows: use when 2+ repos share a pattern.
- Self-hosted runners: use for privileged or heavy workloads.
- Security scanning: use for high-risk repos and release pipelines.

## Non-Negotiables

- Pin action versions (no `@latest`).
- Minimize permissions with `permissions:`.
- Use secrets for sensitive values.

## Read These References When Needed

- Test workflows: `references/test-workflow.md`
- Docker build and push: `references/docker-build-push.md`
- Kubernetes deploy: `references/k8s-deploy.md`
- Matrix builds: `references/matrix-build.md`
- Reusable workflows: `references/reusable-workflows.md`
- Security scanning: `references/security-scanning.md`
- Deployment approvals: `references/deployment-approvals.md`
- Workflow best practices: `references/best-practices.md`
