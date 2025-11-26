"""
Unit tests for service.py - CommentService class.
"""
import unittest
from unittest.mock import Mock, patch
from models import Comment
from service import CommentService
from constants import OperationType


class TestCommentService(unittest.TestCase):
    """Test cases for the CommentService class."""

    def setUp(self):
        """Set up test fixtures before each test."""
        self.test_comment = Comment(
            id="test_001",
            user_id="user_123",
            content="Test comment",
            timestamp="2025-11-26T10:00:00",
            score=0
        )

    @patch('service.mongo_connection')
    def test_comment_service_initialization(self, mock_connection):
        """Test CommentService initialization."""
        mock_collection = Mock()
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()

        self.assertIsNotNone(service.collection)
        mock_connection.get_collection.assert_called_once()

    @patch('service.mongo_connection')
    def test_add_comment_success(self, mock_connection):
        """Test successfully adding a comment."""
        mock_collection = Mock()
        mock_collection.insert_one.return_value.inserted_id = "new_id_123"
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.add(self.test_comment)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, "new_id_123")
        mock_collection.insert_one.assert_called_once()

    @patch('service.mongo_connection')
    def test_add_comment_failure(self, mock_connection):
        """Test adding a comment when database operation fails."""
        mock_collection = Mock()
        mock_collection.insert_one.side_effect = Exception("Database error")
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.add(self.test_comment)

        self.assertIsNone(result)

    @patch('service.mongo_connection')
    def test_update_comment_success(self, mock_connection):
        """Test successfully updating a comment score."""
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.modified_count = 1
        mock_collection.update_one.return_value = mock_result
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.update(self.test_comment, 85.5)

        self.assertIsNotNone(result)
        self.assertEqual(result.score, 85.5)
        mock_collection.update_one.assert_called_once_with(
            {"id": "test_001"},
            {"$set": {"score": 85.5}}
        )

    @patch('service.mongo_connection')
    def test_update_comment_failure(self, mock_connection):
        """Test updating a comment when database operation fails."""
        mock_collection = Mock()
        mock_collection.update_one.side_effect = Exception("Database error")
        mock_connection.get_collection.return_value = mock_connection
        service = CommentService()

        with self.assertRaises(Exception):
            service.update(self.test_comment, 85.5)

    @patch('service.mongo_connection')
    def test_delete_comment_success(self, mock_connection):
        """Test successfully deleting a comment."""
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_result
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.delete("test_001")

        self.assertTrue(result)
        mock_collection.delete_one.assert_called_once_with({"id": "test_001"})

    @patch('service.mongo_connection')
    def test_delete_comment_not_found(self, mock_connection):
        """Test deleting a comment that doesn't exist."""
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.deleted_count = 0
        mock_collection.delete_one.return_value = mock_result
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.delete("non_existent_id")

        self.assertFalse(result)

    @patch('service.mongo_connection')
    def test_delete_comment_failure(self, mock_connection):
        """Test deleting a comment when database operation fails."""
        mock_collection = Mock()
        mock_collection.delete_one.side_effect = Exception("Database error")
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()

        with self.assertRaises(Exception):
            service.delete("test_001")

    @patch('service.mongo_connection')
    def test_process_ops_create(self, mock_connection):
        """Test process_ops with create operation."""
        mock_collection = Mock()
        mock_collection.insert_one.return_value.inserted_id = "new_id"
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.process_ops(self.test_comment, "create", 75.0)

        self.assertIsNotNone(result)
        mock_collection.insert_one.assert_called_once()


    @patch('service.mongo_connection')
    def test_process_ops_update(self, mock_connection):
        """Test process_ops with update operation."""
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.modified_count = 1
        mock_collection.update_one.return_value = mock_result
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.process_ops(self.test_comment, "update", 90.0)

        self.assertIsNotNone(result)
        self.assertEqual(result.score, 90.0)

    @patch('service.mongo_connection')
    def test_process_ops_update_without_score(self, mock_connection):
        """Test process_ops update without providing score."""
        mock_collection = Mock()
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.process_ops(self.test_comment, "update", None)

        self.assertIsNone(result)

    @patch('service.mongo_connection')
    def test_process_ops_delete(self, mock_connection):
        """Test process_ops with delete operation."""
        mock_collection = Mock()
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_result
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.process_ops(self.test_comment, "delete")

        self.assertTrue(result)


    @patch('service.mongo_connection')
    def test_process_ops_invalid_operation(self, mock_connection):
        """Test process_ops with invalid operation type."""
        mock_collection = Mock()
        mock_connection.get_collection.return_value = mock_collection

        service = CommentService()
        result = service.process_ops(self.test_comment, "invalid_op", 75.0)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

