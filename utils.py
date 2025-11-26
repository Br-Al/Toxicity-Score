from configure_logging import get_logger
import random
import time, json
from rabbitmq.publishers.message_publisher import BasicMessagePublisher
from models import Message
from config import settings
from constants import QueueName, ExchangeType



logging = get_logger(__name__)


def simulate_scoring(min_duration: int=2, max_duration: int=15) -> dict:
    """
    Simulate a scoring process that takes a random duration between min_duration and max_duration seconds.
    :param min_duration: minimum duration in seconds (int)
    :param max_duration: maximum duration in seconds (int)
    :return: dict with scoring result
    """
    duration = random.randint(min_duration, max_duration)
    start_time = time.time()
    logging.info(f"Scoring started, will take approximately {duration} seconds.")
    time.sleep(duration)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Scoring completed in {elapsed_time:.2f} seconds.")
    result = {
        "status": "completed",
        "duration_seconds": elapsed_time,
        "score": random.uniform(0, 100)  # Simulated score
    }

    return result

def publish_result(message: Message):
    """
    Publish the result message to RabbitMQ.
    :param message: Message object
    """
    try:
        logging.info("Publishing result message", message_id=message.message_id, status=message.status)
        publisher = BasicMessagePublisher()
        # Declare exchange and queue if not already declared
        publisher.declare_exchange(settings.RABBITMQ_PUBLISHER_EXCHANGE, exchange_type=ExchangeType.TOPIC)
        publisher.bind_queue(
            queue_name=QueueName.PROCESSED_TEXTS,
            exchange_name=settings.RABBITMQ_PUBLISHER_EXCHANGE,
            routing_key=settings.RABBITMQ_PUBLISHER_ROUTING_KEY,
        )
        # Publish message
        publisher.publish(
            exchange_name=settings.RABBITMQ_PUBLISHER_EXCHANGE,
            routing_key=settings.RABBITMQ_PUBLISHER_ROUTING_KEY,
            body=message.__dict__
        )

        logging.info("Message published successfully", body=message)
    except Exception as e:
        logging.error("Error publishing message", body=message, exc_info=True)


def to_dict(body) -> dict:
    """
    Convert RabbitMQ message body from bytes to dict.
    :param body: bytes message body
    :return: dict representation of the message
    """
    try:
        converted = json.loads(body)
        if isinstance(converted, dict):
            return converted
        to_dict(converted)
    except json.JSONDecodeError:
        logging.error("Failed to decode RabbitMQ message body as JSON", exc_info=True)
        return {}