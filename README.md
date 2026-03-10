# aiokafka-client

Reusable async Kafka consumer/producer with SSL/SASL support and structured logging.

## Setup

```bash
uv venv
source .venv/bin/activate
uv sync
```

## Configuration

```bash
cp .env.example .env
```

## Run

```bash
# Consumer loop
uv run python -m app.main

# Publish messages manually
uv run python -m scripts.publish
```

## Extend

Subclass `KafkaClient` to add domain messages:

```python
from app.kafka_client import KafkaClient

class AppKafkaClient(KafkaClient):
    async def queue_index_file(self, file_data: dict) -> None:
        await self._send({**file_data, "type": "index_file"}, key=f"file_{file_data['id']}")

    async def queue_delete_file(self, file_id: int, project_id: int) -> None:
        await self._send(
            {"type": "delete_file", "id": file_id, "project_id": project_id},
            key=f"file_{file_id}",
        )
```

## Structure

```
app/
  kafka_client/    # BaseConsumer, BaseProducer, KafkaClient, KafkaConfig
  core/            # AppConfig, logger
  enums/           # AppMode
  main.py          # Consume loop reference
scripts/
  publish.py       # Manual publish reference
```
