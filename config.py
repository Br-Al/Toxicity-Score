from pydantic import model_validator
from pydantic_settings import BaseSettings


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
    RABBITMQ_START_CONSUMING: bool = False
    # RabbitMQ PUBLISHER for outgoing messages
    RABBITMQ_PUBLISHER_EXCHANGE: str = ""
    RABBITMQ_PUBLISHER_EXCHANGE_TYPE: str = ""
    RABBITMQ_PUBLISHER_ROUTING_KEY: str = ""
    RABBITMQ_PUBLISHER_QUEUE: str = ""
    PUBLISH_SAMPLE_MESSAGES: bool = False

    LOG_LEVEL: str = "INFO"
    LOGGING_PATH: str = "./logs"
    LOGGING_FILE: str = "app.log"
    # MONGODB Settings
    MONGODB_USER: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_DB_NAME: str = "toxicity_score"
    MONGODB_HOST: str = "localhost"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
