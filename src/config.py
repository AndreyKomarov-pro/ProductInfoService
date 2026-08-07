import os

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_url: PostgresDsn

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "product-info-consumer"
    kafka_topics: list[str] = ["users"]
    kafka_topic_dlq: str = "dlq"

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            ".env",
        )
    )


settings = Settings()
