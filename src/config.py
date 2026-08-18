import os

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_url: PostgresDsn

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "product-info-consumer"
    kafka_topics: list[str] = ["users"]
    kafka_dlq_suffix: str = "dlq"
    kafka_consumer_max_retries: int = 3
    kafka_consumer_retry_delay: float = 1.0

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            ".env",
        )
    )


settings = Settings()
