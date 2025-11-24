from config import settings
from configure_logging import configure_logging
import os
from dotenv import load_dotenv
from rabbitmq.consumers.message_consumer import BasicMessageConsumer
import threading
from multiprocessing import Process, Event

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

configure_logging(settings)



if __name__ == '__main__':
    pass


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


def run_consumer():
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

