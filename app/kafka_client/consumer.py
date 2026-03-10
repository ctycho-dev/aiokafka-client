import json
from json.decoder import JSONDecodeError

from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context

from app.core.config import KafkaConfig


class BaseConsumer(AIOKafkaConsumer):

    def __init__(
        self, topic: str | list[str],
        config: KafkaConfig,
        client_id: str
    ):
        ssl_context = create_ssl_context(cafile=config.cafile)

        super().__init__(
            *([topic] if isinstance(topic, str) else topic),
            client_id=client_id,
            bootstrap_servers=config.bootstrap_servers,
            group_id=config.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            value_deserializer=self._deserializer,
            security_protocol=config.security_protocol,
            sasl_mechanism=config.sasl_mechanism,
            sasl_plain_username=config.sasl_plain_username,
            sasl_plain_password=config.sasl_plain_password,
            ssl_context=ssl_context,
        )

    @staticmethod
    def _deserializer(message: bytes) -> dict | str:
        try:
            return json.loads(message.decode("utf-8"))
        except JSONDecodeError:
            return message.decode("utf-8") if isinstance(message, bytes) else message
