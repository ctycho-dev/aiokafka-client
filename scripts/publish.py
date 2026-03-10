"""
Manually publish messages to a Kafka topic.
Usage:
    python scripts/publish.py
"""
import asyncio

from app.kafka_client import KafkaClient
from app.core.config import KafkaConfig
from app.core.logger import get_logger

logger = get_logger(__name__)


async def main():
    config = KafkaConfig()
    client = KafkaClient(config, client_id="rag-publisher")

    try:
        await client.start()

        # ── single message ────────────────────────────────────────────
        await client._send(
            payload={"type": "index_file", "id": 1, "project_id": 7,
                     "filename": "doc.pdf", "file_key": "1-doc.pdf"},
            key="file_1",
        )

        # ── batch ─────────────────────────────────────────────────────
        await client._send_batch(
            payloads=[
                {"type": "index_page", "id": 1, "project_id": 7,
                 "title": "Title", "question": "Q?", "answer": "A."},
                {"type": "index_page", "id": 2, "project_id": 7,
                 "title": "Title 2", "question": "Q2?", "answer": "A2."},
            ],
            keys=["page_1", "page_2"],
        )

    finally:
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
