import pika.exceptions
from rabbitmq.connection import RabbitMQConnection
from pika import BasicProperties
from config import settings
import logging
import time


class BasicMessageConsumer(RabbitMQConnection):



    def start_consuming(self, queue_name):

        while True:
            try:
                self.ensure_connection()
                logging.info("Starting message consumption...")
                channel = self.channel
                channel.basic_qos(prefetch_count=settings.RABBITMQ_PREFETCH_COUNT)
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=self.on_message,
                    auto_ack=False
                )
                channel.start_consuming()
            except pika.exceptions.AMQPConnectionError:
                logging.error("Connection to RabbitMQ lost. Reconnecting...", exc_info=True)
                time.sleep(settings.RABBITMQ_PAUSE)
                continue
            except pika.exceptions.ChannelClosedByBroker:
                logging.error("Channel closed by broker. Re-establishing channel...", exc_info=True)
                time.sleep(settings.RABBITMQ_PAUSE)
                continue
            except Exception:
                logging.error("An unexpected error occurred during message consumption.", exc_info=True)
                time.sleep(settings.RABBITMQ_PAUSE)
                continue

    def on_message(self, ch, method, properties: BasicProperties, body):
        logging.info(f"Received message: {body}")
        # Process the message here
        ch.basic_ack(delivery_tag=method.delivery_tag)


    def get_message(self, queue):
        self.ensure_connection()
        method_frame, header_frame, body = self.channel.basic_get(queue=queue, auto_ack=False)
        if method_frame:
            logging.info(f"Retrieved message: {body}")
            self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            return body
        else:
            logging.info("No message available in the queue.")
            return None


