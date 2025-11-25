from config import settings
from configure_logging import configure_logging
import os
from datetime import datetime
from random import randint, choice
import string
from dotenv import load_dotenv
from rabbitmq.consumers.message_consumer import BasicMessageConsumer
from rabbitmq.publishers.message_publisher import BasicMessagePublisher
import threading
from multiprocessing import Process, Event
from configure_logging import get_logger

logging = get_logger(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

if settings.LOGGING_PATH and not os.path.exists(settings.LOGGING_PATH):
    os.makedirs(settings.LOGGING_PATH)


configure_logging(settings)


def start_rabbitmq_consumer():
    consumer = BasicMessageConsumer()
    # Declare exchange and queue based on settings
    consumer.declare_exchange(
        exchange_name=settings.RABBITMQ_CONSUMER_EXCHANGE,
        exchange_type=settings.RABBITMQ_CONSUMER_EXCHANGE_TYPE
    )

    consumer.bind_queue(
        queue_name=settings.RABBITMQ_CONSUMER_QUEUE,
        exchange_name=settings.RABBITMQ_CONSUMER_EXCHANGE,
        routing_key=settings.RABBITMQ_CONSUMER_ROUTING_KEY
    )

    consumer.start_consuming(queue_name=settings.RABBITMQ_CONSUMER_QUEUE)

    consumer.close()

def start_rabbitmq_publisher():
     publisher = BasicMessagePublisher()
     publisher.declare_exchange(
        exchange_name=settings.RABBITMQ_PUBLISHER_EXCHANGE,
        exchange_type=settings.RABBITMQ_PUBLISHER_EXCHANGE_TYPE
     )
     publisher.bind_queue(
        queue_name=settings.RABBITMQ_CONSUMER_QUEUE,
        exchange_name=settings.RABBITMQ_PUBLISHER_EXCHANGE,
        routing_key=settings.RABBITMQ_PUBLISHER_ROUTING_KEY
     )

     # Publish a number of sample messages
     sample_messages_count = settings.SAMPLE_MESSAGES_COUNT
     logging.debug(f"Publishing {sample_messages_count} sample messages to RabbitMQ")
     messages = [
         {
                "id": f"msg_{i+1}",
                "user_id": f"u_{randint(1000, 9999)}",
                "text": ''.join(choice(string.ascii_letters + string.digits) for _ in range(20)),
                "timestamp": datetime.utcnow().isoformat(),
                "type": choice(["create", "update", "delete"])
         } for i in range(sample_messages_count)
    ]
     for msg in messages:
        routing_key = f"{settings.RABBITMQ_PUBLISHER_ROUTING_KEY}.{msg.get('id')}.{msg.get('type')}"
        publisher.publish(
            exchange_name=settings.RABBITMQ_PUBLISHER_EXCHANGE,
            routing_key=routing_key,
            body=msg
        )

     publisher.close()

def run_consumer(event, *args, **kwargs):

    logging.info("Starting RabbitMQ Consumer Process")
    consumers = [
        start_rabbitmq_consumer
    ]

    threads = []

    for consumer in consumers:
        thread = threading.Thread(target=consumer)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def run_publisher(event, *args, **kwargs):

    logging.info("Starting RabbitMQ Publisher Process")
    publishers = [
        start_rabbitmq_publisher
    ]

    threads = []

    for publisher in publishers:
        thread = threading.Thread(target=publisher)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    started_event = Event()
    process_list = []
    if settings.RABBITMQ_START_CONSUMING:
        process_list.append(Process(target=run_consumer, args=(started_event,), name="RabbitMQ Consumer Process"))
    if settings.PUBLISH_SAMPLE_MESSAGES:
        process_list.append(Process(target=run_publisher, args=(started_event,), name="RabbitMQ Publisher Process"))

    for proc in process_list:
        proc.start()
        print(f"Process name: {proc.name}, PID: {proc.pid}")

    for proc in process_list:
        proc.join()