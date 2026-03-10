import json

from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context

from app.core.config import KafkaConfig


class BaseProducer(AIOKafkaProducer):

    def __init__(self, config: KafkaConfig, client_id: str):
        ssl_context = create_ssl_context(cafile=config.cafile)

        super().__init__(
            client_id=client_id,
            bootstrap_servers=config.bootstrap_servers,
            security_protocol=config.security_protocol,
            sasl_mechanism=config.sasl_mechanism,
            sasl_plain_username=config.sasl_plain_username,
            sasl_plain_password=config.sasl_plain_password,
            ssl_context=ssl_context,
            value_serializer=self.serializer,
        )

    @staticmethod
    def serializer(message):
        return json.dumps(message).encode("utf-8")
