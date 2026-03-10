from typing import Any

from app.core.config import KafkaConfig
from app.kafka_client.consumer import BaseConsumer
from app.kafka_client.producer import BaseProducer
from app.core.logger import get_logger

logger = get_logger(__name__)


class KafkaClient:

    def __init__(self, config: KafkaConfig, client_id: str = "kafka-client") -> None:
        self._config = config
        self._client_id = client_id
        self._producer: BaseProducer | None = None
        self._consumer: BaseConsumer | None = None

    # ── lifecycle ───────────────────────────────────────────────────────

    async def start(self) -> None:
        self._producer = BaseProducer(self._config, self._client_id)
        await self._producer.start()
        logger.info("[KAFKA] Producer started bootstrap=%s", self._config.bootstrap_servers)

        self._consumer = BaseConsumer(self._config.tasks_topic, self._config, self._client_id)
        await self._consumer.start()
        logger.info("[KAFKA] Consumer started topic=%s group=%s",
                    self._config.tasks_topic, self._config.group_id)

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
            logger.info("[KAFKA] Consumer stopped")
        if self._producer:
            await self._producer.stop()
            self._producer = None
            logger.info("[KAFKA] Producer stopped")

    # ── accessors ───────────────────────────────────────────────────────

    @property
    def consumer(self) -> BaseConsumer:
        if self._consumer is None:
            raise RuntimeError("Consumer not started — call start() first")
        return self._consumer

    @property
    def producer(self) -> BaseProducer:
        if self._producer is None:
            raise RuntimeError("Producer not started — call start() first")
        return self._producer

    # ── transport ───────────────────────────────────────────────────────

    async def _send(self, payload: dict[str, Any], key: str | None = None) -> None:
        encoded_key = key.encode() if key else None
        await self.producer.send_and_wait(
            self._config.tasks_topic,
            key=encoded_key,
            value=payload,
        )
        logger.info("[KAFKA] Sent type=%s id=%s", payload.get("type"), payload.get("id"))

    async def _send_batch(self, payloads: list[dict[str, Any]], keys: list[str] | None = None) -> None:
        """Buffer all messages, single flush — one broker round-trip."""
        for i, payload in enumerate(payloads):
            key = keys[i].encode() if keys and i < len(keys) else None
            await self.producer.send(self._config.tasks_topic, key=key, value=payload)
        await self.producer.flush()
        logger.info("[KAFKA] Batch sent count=%d", len(payloads))

    # ── health ───────────────────────────────────────────────────────────

    async def ping(self) -> bool:
        try:
            if self._producer is None:
                return False
            await self._producer.client._wait_on_metadata(self._config.tasks_topic, 5.0)
            return True
        except Exception:
            return False
