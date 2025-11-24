import pika
import logging


class RabbitMQConnection:

    def __init__(self):
        pika_url = f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.vhost}"
        self.parameters = pika.URLParameters(pika_url)
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        try:
            logging.info("Connecting to RabbitMQ server...")
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            logging.info("Connected to RabbitMQ server successfully.")
        except Exception as e:
            logging.error(f"Failed to connect to RabbitMQ server", exc_info=True)


    def ensure_connection(self):
        if not self.connection or self.connection.is_closed:
            logging.info("RabbitMQ Connection lost. Reconnecting to RabbitMQ server...")
            self._connect()

    def declare_exchange(self, exchange_name, exchange_type='direct', durable=True):
        self.ensure_connection()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=durable)
        logging.info(f"Declared exchange: {exchange_name}")

    def bind_queue(self, queue_name, exchange_name, routing_key):
        try:
            logging.info(f"Binding queue {queue_name} to exchange {exchange_name} with routing key {routing_key}")
            self.ensure_connection()
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=routing_key)
            logging.info(f"Bound queue {queue_name} to exchange {exchange_name} with routing key {routing_key}")

        except Exception as e:
            logging.error(f"Failed to bind queue {queue_name} to exchange {exchange_name}", exc_info=True)


    def delete_queue(self, queue_name):
        try:
            logging.info(f"Deleting queue: {queue_name}")
            self.ensure_connection()
            self.channel.queue_delete(queue=queue_name)
            logging.info(f"Deleted queue: {queue_name}")
        except Exception as e:
            logging.error(f"Failed to delete queue {queue_name}", exc_info=True)

    def close(self):
        if self.connection and not self.connection.is_closed:
            logging.info("Closing RabbitMQ connection...")
            self.channel.close()
            self.connection.close()
            logging.info("RabbitMQ connection closed.")