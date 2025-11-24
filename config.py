from pydantic import model_validator
from pydantic_settings import BaseSettings
import logging


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
    # RabbitMQ Consumer for incoming messages
    RABBITMQ_CONSUMER_QUEUE: str = ""
    RABBITMQ_CONSUMER_EXCHANGE: str = ""
    RABBITMQ_CONSUMER_ROUTING_KEY: str = ""
    RABBITMQ_CONSUMER_EXCHANGE_TYPE: str = ""
    # RabbitMQ Producer for outgoing messages
    RABBITMQ_PRODUCER_EXCHANGE: str = ""
    RABBITMQ_PRODUCER_EXCHANGE_TYPE: str = ""
    RABBITMQ_PRODUCER_ROUTING_KEY: str = ""
    RABBITMQ_PRODUCER_QUEUE: str = ""

    LOG_LEVEL: str = "INFO"
    LOGGING_PATH: str = "./logs"
    LOGGING_FILE: str = "app.log"
    # MONGODB Settings
    MONGODB_URI: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
