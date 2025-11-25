import pika.exceptions
from rabbitmq.connection import RabbitMQConnection
from pika import BasicProperties
from config import settings
import time
import json
from models import Comment, Message
from utils import CommentService, simulate_scoring, publish_result
from configure_logging import get_logger

logging = get_logger(__name__)


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

    @staticmethod
    def on_message(ch, method, properties: BasicProperties, body):
        logging.info(f"Received message", body=body, properties=properties, routing_key=method.routing_key)
        body = json.loads(body)
        comment = Comment(
            id=body.get("id"),
            content=body.get("text"),
            user_id=body.get("user_id"),
            timestamp=body.get("timestamp"),
            score=body.get("score", 0)
        )
        ops = body.get("type", "create").lower()
        score = simulate_scoring().get('score')
        message_result = Message(
            message_id=comment.id,
            status="processed",
            type=ops,
        )
        try:
            comment_service = CommentService()
            # Process the message (placeholder for actual processing logic)
            logging.info(f"Processing message", message=body)
            result = comment_service.process_ops(comment, ops, score)
            publish_result(message_result)
            # Acknowledge the message after successful processing
            if result:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logging.info("Message acknowledged.")
                return
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=settings.RABBITMQ_REQUEUE_ON_FAIL)
            logging.warning("Message processing failed, message not acknowledged.")
        except json.JSONDecodeError:
            logging.error("Failed to decode message body as JSON.", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=settings.RABBITMQ_REQUEUE_ON_FAIL)
            message_result.status = "failed"
            publish_result(message_result)
        except Exception as e:
            logging.error("Failed to process message.", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=settings.RABBITMQ_REQUEUE_ON_FAIL)
            message_result.status = "failed"
            publish_result(message_result)



