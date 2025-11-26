from configure_logging import get_logger
import pika
import json
from rabbitmq.connection import RabbitMQConnection
logging = get_logger(__name__)


class BasicMessagePublisher(RabbitMQConnection):
    def publish(self, exchange_name, routing_key, body, properties: pika.BasicProperties=None):
        try:
            self.ensure_connection()
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(body),
                properties=properties
            )
            self.channel.basic_qos(prefetch_count=1)
            logging.info("RabbitMQ message published", exchange=exchange_name, routing_key=routing_key, body=body)
        except Exception as e:
            logging.error("Failed to publish message to RabbitMQ", exc_info=True)

publisher = BasicMessagePublisher()