from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="KAFKA_",
        case_sensitive=False,
        extra="ignore",
    )

    bootstrap_servers: str
    tasks_topic: str = "rag.processing"
    dlq_topic: str = "rag.processing.dlq"
    group_id: str = "rag-worker"
    max_retries: int = 3
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: str | None = None
    sasl_plain_username: str | None = None
    sasl_plain_password: str | None = None
    cafile: str | None = None
