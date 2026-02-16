# PostgreSQL Event Store Schema

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id VARCHAR(255) NOT NULL,
    stream_type VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    version BIGINT NOT NULL,
    global_position BIGSERIAL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_stream_version UNIQUE (stream_id, version)
);

CREATE INDEX idx_events_stream_id ON events(stream_id, version);
CREATE INDEX idx_events_global_position ON events(global_position);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_created_at ON events(created_at);

CREATE TABLE snapshots (
    stream_id VARCHAR(255) PRIMARY KEY,
    stream_type VARCHAR(255) NOT NULL,
    snapshot_data JSONB NOT NULL,
    version BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE subscription_checkpoints (
    subscription_id VARCHAR(255) PRIMARY KEY,
    last_position BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```
