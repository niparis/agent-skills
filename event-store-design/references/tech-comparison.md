# Technology Comparison

| Technology       | Best For                  | Limitations                      |
| ---------------- | ------------------------- | -------------------------------- |
| EventStoreDB     | Pure event sourcing       | Single-purpose                   |
| PostgreSQL       | Existing Postgres stack   | Manual implementation            |
| Kafka            | High-throughput streaming | Not ideal for per-stream queries |
| DynamoDB         | Serverless, AWS-native    | Query limitations                |
| Marten           | .NET ecosystems           | .NET specific                    |
