# Deployment with Approvals

```yaml
name: Deploy to Production

on:
  push:
    tags: [ "v*" ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.example.com
    steps:
      - uses: actions/checkout@v4
      - name: Deploy application
        run: |
          echo "Deploying to production..."
```
