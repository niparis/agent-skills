# Implementation Sketches

## Python (Append Events with Optimistic Concurrency)

```python
class EventStore:
    def __init__(self, pool):
        self.pool = pool

    async def append(self, stream_id, events, expected_version=None):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                if expected_version is not None:
                    current = await conn.fetchval(
                        "SELECT COALESCE(MAX(version), 0) FROM events WHERE stream_id = $1",
                        stream_id,
                    )
                    if current != expected_version:
                        raise ConcurrencyError("version mismatch")

                start_version = await conn.fetchval(
                    "SELECT COALESCE(MAX(version), 0) + 1 FROM events WHERE stream_id = $1",
                    stream_id,
                )
                for i, event in enumerate(events):
                    await conn.execute(
                        """
                        INSERT INTO events (id, stream_id, stream_type, event_type,
                                            event_data, metadata, version, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                        """,
                        event.id,
                        stream_id,
                        event.stream_type,
                        event.event_type,
                        event.data,
                        event.metadata,
                        start_version + i,
                    )
```

## EventStoreDB (Core API)

```python
client = EventStoreDBClient(uri="esdb://localhost:2113?tls=false")
client.append_to_stream(stream_name, events, current_version=expected_revision)
```

## DynamoDB (Core Pattern)

```python
item = {
    "PK": f"STREAM#{stream_id}",
    "SK": f"VERSION#{version:020d}",
    "event_id": event_id,
    "event_type": event_type,
    "event_data": event_data,
}
table.put_item(Item=item)
```
