"""
Unit tests for Pydantic models (Comment and Message).
"""
import unittest
from datetime import datetime
from models import Comment, Message
from pydantic import ValidationError


class TestCommentModel(unittest.TestCase):
    """Test cases for the Comment model."""

    def setUp(self):
        """Set up test data."""
        self.valid_comment_data = {
            "id": "test_001",
            "user_id": "user_123",
            "content": "This is a test comment",
            "timestamp": "2025-11-25T10:00:00",
            "score": 75.5
        }

    def test_comment_creation_with_valid_data(self):
        """Test creating a Comment with valid data."""
        comment = Comment(**self.valid_comment_data)
        self.assertEqual(comment.id, "test_001")
        self.assertEqual(comment.user_id, "user_123")
        self.assertEqual(comment.content, "This is a test comment")
        self.assertEqual(comment.timestamp, "2025-11-25T10:00:00")
        self.assertEqual(comment.score, 75.5)
        self.assertIsInstance(comment.created_at, datetime)
        self.assertIsNone(comment.deleted_at)
        self.assertIsNone(comment.updated_at)

    def test_comment_score_validation_in_range(self):
        """Test that score must be between 0 and 100."""
        # Valid scores
        comment = Comment(**{**self.valid_comment_data, "score": 0})
        self.assertEqual(comment.score, 0)

        comment = Comment(**{**self.valid_comment_data, "score": 100})
        self.assertEqual(comment.score, 100)

        comment = Comment(**{**self.valid_comment_data, "score": 50.5})
        self.assertEqual(comment.score, 50.5)

    def test_comment_score_validation_out_of_range(self):
        """Test that score outside 0-100 raises ValidationError."""
        # Score too low
        with self.assertRaises(ValidationError):
            Comment(**{**self.valid_comment_data, "score": -1})

        # Score too high
        with self.assertRaises(ValidationError):
            Comment(**{**self.valid_comment_data, "score": 101})

    def test_comment_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        required_fields = ["id", "user_id", "content", "timestamp", "score"]

        for field in required_fields:
            data = {k: v for k, v in self.valid_comment_data.items() if k != field}
            with self.assertRaises(ValidationError):
                Comment(**data)

    def test_comment_optional_fields(self):
        """Test that optional fields work correctly."""
        from datetime import UTC
        comment = Comment(**self.valid_comment_data)

        # Update optional fields
        now = datetime.now(UTC)
        comment.updated_at = now
        comment.deleted_at = now

        self.assertEqual(comment.updated_at, now)
        self.assertEqual(comment.deleted_at, now)

    def test_comment_default_created_at(self):
        """Test that created_at is automatically set."""
        from datetime import UTC
        before = datetime.now(UTC)
        comment = Comment(**self.valid_comment_data)
        after = datetime.now(UTC)

        self.assertIsInstance(comment.created_at, datetime)
        self.assertGreaterEqual(comment.created_at, before)
        self.assertLessEqual(comment.created_at, after)


class TestMessageModel(unittest.TestCase):
    """Test cases for the Message model."""

    def setUp(self):
        """Set up test data."""
        self.valid_message_data = {
            "type": "create",
            "status": "processed",
            "message_id": "msg_001"
        }

    def test_message_creation_with_valid_data(self):
        """Test creating a Message with valid data."""
        message = Message(**self.valid_message_data)
        self.assertEqual(message.type, "create")
        self.assertEqual(message.status, "processed")
        self.assertEqual(message.message_id, "msg_001")
        self.assertIsNotNone(message.id)
        self.assertIsInstance(message.processed_at, str)

    def test_message_auto_generated_id(self):
        """Test that message ID is auto-generated as UUID."""
        message = Message(**self.valid_message_data)
        self.assertIsNotNone(message.id)
        self.assertIsInstance(message.id, str)
        # UUID format check (basic)
        self.assertTrue(len(message.id) > 0)

    def test_message_default_processed_at(self):
        """Test that processed_at is automatically set."""
        message = Message(**self.valid_message_data)
        self.assertIsNotNone(message.processed_at)
        self.assertIsInstance(message.processed_at, str)
        # Should be in ISO format
        datetime.fromisoformat(message.processed_at)

    def test_message_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        required_fields = ["type", "status", "message_id"]

        for field in required_fields:
            data = {k: v for k, v in self.valid_message_data.items() if k != field}
            with self.assertRaises(ValidationError):
                Message(**data)

    def test_message_with_custom_id(self):
        """Test creating message with custom _id."""
        custom_data = {
            **self.valid_message_data,
            "_id": "custom_id_123"
        }
        message = Message(**custom_data)
        self.assertEqual(message.id, "custom_id_123")

    def test_message_types(self):
        """Test different message types."""
        message_types = ["create", "update", "delete", "processed", "failed"]

        for msg_type in message_types:
            message = Message(**{**self.valid_message_data, "type": msg_type})
            self.assertEqual(message.type, msg_type)

    def test_message_statuses(self):
        """Test different message statuses."""
        statuses = ["processed", "failed", "pending", "error"]

        for status in statuses:
            message = Message(**{**self.valid_message_data, "status": status})
            self.assertEqual(message.status, status)


if __name__ == '__main__':
    unittest.main()

