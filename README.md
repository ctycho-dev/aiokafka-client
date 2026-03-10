# aiokafka-client

Reusable async Kafka consumer/producer with SSL/SASL support.

## Install

```bash
pip install git+https://github.com/yourname/aiokafka-client.git
```

## Usage

### Config
```python
from kafka_client import KafkaConfig

config = KafkaConfig(
    bootstrap_servers="localhost:9092",
    topic="my.topic",
    group_id="my-group",
    # For Yandex Cloud / SASL_SSL:
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username="user",
    sasl_plain_password="pass",
    cafile="/path/to/YandexInternalRootCA.crt",
)
```

### Producer only
```python
client = KafkaClient(config)
await client.start()
await client._send({"type": "my_event", "id": 1})
await client.stop()
```

### Producer + Consumer
```python
await client.start(consume=True)
msg = await client.consumer.getone()
```

### Subclass for domain messages
```python
class AppKafkaClient(KafkaClient):
    async def queue_index_file(self, file_data: dict) -> None:
        await self._send({**file_data, "type": "index_file"}, key=f"file_{file_data['id']}")
```

## Local vs Yandex Cloud

| Env | `security_protocol` | credentials | `cafile` |
|-----|-------------------|-------------|--------|
| Local Docker | `PLAINTEXT` | not needed | not needed |
| Yandex Cloud | `SASL_SSL` | required | required |
