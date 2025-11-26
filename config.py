from pydantic import model_validator, field_validator
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # RabbitMQ Connection Settings
    RABBITMQ_HOST: str = ""
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USERNAME: str = ""
    RABBITMQ_PASSWORD: str = ""
    RABBITMQ_VHOST: str = "/"
    # RabbitMQ General Settings
    RABBITMQ_HEARTBEAT: int = 60
    RABBITMQ_BLOCKED_CONNECTION_TIMEOUT: int = 30
    RABBITMQ_PREFETCH_COUNT: int = 1
    RABBITMQ_MAX_RETRIES: int = 5
    RABBITMQ_PAUSE: int = 5
    # RabbitMQ Consumer for incoming messages
    RABBITMQ_CONSUMER_QUEUE: str = ""
    RABBITMQ_CONSUMER_EXCHANGE: str = ""
    RABBITMQ_CONSUMER_ROUTING_KEY: str = ""
    RABBITMQ_CONSUMER_EXCHANGE_TYPE: str = ""
    RABBITMQ_START_CONSUMING: bool = False
    # RabbitMQ PUBLISHER for outgoing messages
    RABBITMQ_PUBLISHER_EXCHANGE: str = ""
    RABBITMQ_PUBLISHER_EXCHANGE_TYPE: str = ""
    RABBITMQ_PUBLISHER_ROUTING_KEY: str = ""
    RABBITMQ_PUBLISHER_QUEUE: str = ""
    PUBLISH_SAMPLE_MESSAGES: bool = False
    SAMPLE_MESSAGES_COUNT: int = 10
    RABBITMQ_REQUEUE_ON_FAIL: bool = True
    LOG_LEVEL: str = "INFO"
    LOGGING_PATH: str = "./logs"
    LOGGING_FILE: str = "app.log"
    # MONGODB Settings
    MONGODB_USER: str = ""
    MONGODB_MODE: str = "local"
    MONGODB_PASSWORD: str = ""
    MONGODB_DB_NAME: str = "toxicity_score"
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @model_validator(mode='after')
    def validate_rabbitmq_config(self):
        """Validate RabbitMQ configuration when consuming or publishing is enabled."""
        if self.RABBITMQ_START_CONSUMING or self.PUBLISH_SAMPLE_MESSAGES:
            if not self.RABBITMQ_HOST:
                raise ValueError("RABBITMQ_HOST is required when RabbitMQ is enabled")
            if not self.RABBITMQ_USERNAME:
                raise ValueError("RABBITMQ_USERNAME is required when RabbitMQ is enabled")
            if not self.RABBITMQ_PASSWORD:
                raise ValueError("RABBITMQ_PASSWORD is required when RabbitMQ is enabled")
        return self

    @model_validator(mode='after')
    def validate_mongodb_config(self):
        """Validate MongoDB configuration."""
        if not self.MONGODB_HOST:
            raise ValueError("MONGODB_HOST is required")
        if self.MONGODB_MODE == "atlas" and not self.MONGODB_USER:
            raise ValueError("MONGODB_USER is required for Atlas mode")
        return self


settings = Settings()
