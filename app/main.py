"""
Consume loop reference — adapt process_message to your handler dispatch.
"""
import asyncio
import signal

from app.kafka_client import KafkaClient
from app.core.config import KafkaConfig
from app.core.logger import get_logger, setup_logging


logger = get_logger(__name__)


async def process_message(msg) -> None:
    """Replace with your handler dispatch logic."""
    logger.info("Processing type=%s id=%s offset=%s",
                msg.value.get("type"), msg.value.get("id"), msg.offset)


async def main():
    setup_logging()
    config = KafkaConfig()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    client = KafkaClient(config, client_id="rag-worker")
    logger.info('KafkaClient initialised')

    try:
        await client.start()
        consumer = client.consumer

        while not stop_event.is_set():
            try:
                msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            await process_message(msg)
            await consumer.commit()
            logger.info("[CONSUMER] ✓ Committed offset=%s", msg.offset)

    finally:
        await client.stop()
        logger.info("[SHUTDOWN] Worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
