"""
Unit tests for utility functions and CommentService.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import time
from models import Comment, Message
from utils import simulate_scoring, publish_result
from service import CommentService
from database.connection import MongoDBConnection


class TestSimulateScoring(unittest.TestCase):
    """Test cases for the simulate_scoring function."""

    def test_simulate_scoring_returns_dict(self):
        """Test that simulate_scoring returns a dictionary."""
        result = simulate_scoring(min_duration=0, max_duration=1)
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()

