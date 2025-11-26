"""
Integration tests for RabbitMQ message publisher and consumer.
These tests use mocks to avoid requiring actual RabbitMQ connection.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock, call
import json
from rabbitmq.publishers.message_publisher import BasicMessagePublisher
from rabbitmq.consumers.message_consumer import BasicMessageConsumer
from models import Comment, Message
import pika


class TestBasicMessagePublisher(unittest.TestCase):
    """Test cases for the BasicMessagePublisher class."""

    @patch('rabbitmq.publishers.message_publisher.RabbitMQConnection.__init__')
    def test_publisher_initialization(self, mock_init):
        """Test BasicMessagePublisher initialization."""
        mock_init.return_value = None

        publisher = BasicMessagePublisher()

        self.assertIsNotNone(publisher)

    @patch('rabbitmq.publishers.message_publisher.RabbitMQConnection.ensure_connection')
    @patch('rabbitmq.publishers.message_publisher.RabbitMQConnection.__init__')
    def test_publish_message_success(self, mock_init, mock_ensure_connection):
        """Test successfully publishing a message."""
        mock_init.return_value = None
        mock_channel = Mock()

        publisher = BasicMessagePublisher()
        publisher.channel = mock_channel

        test_body = {"id": "test_001", "text": "Test message"}
        publisher.publish(
            exchange_name="test_exchange",
            routing_key="test.key",
            body=test_body
        )

        mock_ensure_connection.assert_called_once()
        mock_channel.basic_publish.assert_called_once()

        # Verify the message body is JSON serialized
        call_args = mock_channel.basic_publish.call_args
        self.assertEqual(call_args[1]['exchange'], "test_exchange")
        self.assertEqual(call_args[1]['routing_key'], "test.key")
        self.assertEqual(json.loads(call_args[1]['body']), test_body)


class TestBasicMessageConsumer(unittest.TestCase):
    """Test cases for the BasicMessageConsumer class."""

    @patch('rabbitmq.consumers.message_consumer.RabbitMQConnection.__init__')
    def test_consumer_initialization(self, mock_init):
        """Test BasicMessageConsumer initialization."""
        mock_init.return_value = None

        consumer = BasicMessageConsumer()

        self.assertIsNotNone(consumer)

    @patch('rabbitmq.consumers.message_consumer.CommentService')
    @patch('rabbitmq.consumers.message_consumer.simulate_scoring')
    @patch('rabbitmq.consumers.message_consumer.publish_result')
    def test_on_message_create_operation(self, mock_publish, mock_scoring, mock_service_class):
        """Test processing a create message."""
        # Setup mocks
        mock_scoring.return_value = {'score': 75.5, 'status': 'completed', 'duration_seconds': 3.2}
        mock_service = Mock()
        mock_service.process_ops.return_value = Mock()  # Successful result
        mock_service_class.return_value = mock_service

        # Mock channel and method
        mock_channel = Mock()
        mock_method = Mock()
        mock_method.delivery_tag = 'test_tag'
        mock_method.routing_key = 'test.key'
        mock_properties = Mock()

        # Message body
        body = json.dumps({
            "id": "msg_001",
            "user_id": "user_123",
            "text": "Test comment",
            "timestamp": "2025-11-25T10:00:00",
            "type": "create"
        })

        # Call on_message
        BasicMessageConsumer.on_message(mock_channel, mock_method, mock_properties, body)

        # Verify comment service was called
        mock_service.process_ops.assert_called_once()

        # Verify message was acknowledged
        mock_channel.basic_ack.assert_called_once_with(delivery_tag='test_tag')

        # Verify result was published
        mock_publish.assert_called_once()

    @patch('rabbitmq.consumers.message_consumer.CommentService')
    @patch('rabbitmq.consumers.message_consumer.simulate_scoring')
    @patch('rabbitmq.consumers.message_consumer.publish_result')
    def test_on_message_update_operation(self, mock_publish, mock_scoring, mock_service_class):
        """Test processing an update message."""
        mock_scoring.return_value = {'score': 82.3, 'status': 'completed', 'duration_seconds': 4.1}
        mock_service = Mock()
        mock_service.process_ops.return_value = Mock()
        mock_service_class.return_value = mock_service

        mock_channel = Mock()
        mock_method = Mock()
        mock_method.delivery_tag = 'test_tag'
        mock_method.routing_key = 'test.key'
        mock_properties = Mock()

        body = json.dumps({
            "id": "msg_002",
            "user_id": "user_456",
            "text": "Updated comment",
            "timestamp": "2025-11-25T11:00:00",
            "type": "update"
        })

        BasicMessageConsumer.on_message(mock_channel, mock_method, mock_properties, body)

        mock_channel.basic_ack.assert_called_once_with(delivery_tag='test_tag')

    @patch('rabbitmq.consumers.message_consumer.CommentService')
    @patch('rabbitmq.consumers.message_consumer.simulate_scoring')
    @patch('rabbitmq.consumers.message_consumer.publish_result')
    def test_on_message_delete_operation(self, mock_publish, mock_scoring, mock_service_class):
        """Test processing a delete message."""
        mock_scoring.return_value = {'score': 0, 'status': 'completed', 'duration_seconds': 2.5}
        mock_service = Mock()
        mock_service.process_ops.return_value = True  # Successful deletion
        mock_service_class.return_value = mock_service

        mock_channel = Mock()
        mock_method = Mock()
        mock_method.delivery_tag = 'test_tag'
        mock_method.routing_key = 'test.key'
        mock_properties = Mock()

        body = json.dumps({
            "id": "msg_003",
            "user_id": "user_789",
            "text": "Comment to delete",
            "timestamp": "2025-11-25T12:00:00",
            "type": "delete"
        })

        BasicMessageConsumer.on_message(mock_channel, mock_method, mock_properties, body)

        mock_channel.basic_ack.assert_called_once_with(delivery_tag='test_tag')

    @patch('rabbitmq.consumers.message_consumer.CommentService')
    @patch('rabbitmq.consumers.message_consumer.simulate_scoring')
    @patch('rabbitmq.consumers.message_consumer.publish_result')
    @patch('rabbitmq.consumers.message_consumer.settings')
    def test_on_message_processing_failure(self, mock_settings, mock_publish, mock_scoring, mock_service_class):
        """Test handling message processing failure."""
        mock_settings.RABBITMQ_REQUEUE_ON_FAIL = True
        mock_scoring.return_value = {'score': 75.5, 'status': 'completed', 'duration_seconds': 3.2}
        mock_service = Mock()
        mock_service.process_ops.return_value = None  # Failed result
        mock_service_class.return_value = mock_service

        mock_channel = Mock()
        mock_method = Mock()
        mock_method.delivery_tag = 'test_tag'
        mock_method.routing_key = 'test.key'
        mock_properties = Mock()

        body = json.dumps({
            "id": "msg_004",
            "user_id": "user_111",
            "text": "Failing comment",
            "timestamp": "2025-11-25T13:00:00",
            "type": "create"
        })

        BasicMessageConsumer.on_message(mock_channel, mock_method, mock_properties, body)

        # Verify message was NOT acknowledged (nack instead)
        mock_channel.basic_ack.assert_not_called()
        mock_channel.basic_nack.assert_called_once_with(delivery_tag='test_tag', requeue=True)

    @patch('rabbitmq.consumers.message_consumer.CommentService')
    @patch('rabbitmq.consumers.message_consumer.simulate_scoring')
    @patch('rabbitmq.consumers.message_consumer.publish_result')
    @patch('rabbitmq.consumers.message_consumer.settings')
    def test_on_message_invalid_json(self, mock_settings, mock_publish, mock_scoring, mock_service_class):
        """Test handling invalid JSON in message body."""
        mock_settings.RABBITMQ_REQUEUE_ON_FAIL = False

        mock_channel = Mock()
        mock_method = Mock()
        mock_method.delivery_tag = 'test_tag'
        mock_method.routing_key = 'test.key'
        mock_properties = Mock()

        # Invalid JSON
        body = "{ invalid json }"

        BasicMessageConsumer.on_message(mock_channel, mock_method, mock_properties, body)

        # Verify message was nacked
        mock_channel.basic_nack.assert_called_once_with(delivery_tag='test_tag', requeue=False)



if __name__ == '__main__':
    unittest.main()

