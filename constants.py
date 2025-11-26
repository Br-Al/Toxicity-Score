"""
Constants and enums for the Toxicity-Score application.
Centralizes all magic strings and configuration values.
"""
from enum import Enum


class OperationType(str, Enum):
    """Message operation types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class MessageStatus(str, Enum):
    """Message processing status."""
    PROCESSED = "processed"
    FAILED = "failed"
    PENDING = "pending"


class CollectionName:
    """MongoDB collection names."""
    COMMENTS = "comments"
    MESSAGES = "messages"
    AUDIT_LOG = "audit_log"


class QueueName:
    """RabbitMQ queue names - can be overridden by config."""
    INCOMING_TEXTS = "q.incoming_texts"
    PROCESSED_TEXTS = "q.processed_texts"


class ExchangeType:
    """RabbitMQ exchange types."""
    DIRECT = "direct"
    TOPIC = "topic"
    FANOUT = "fanout"
    HEADERS = "headers"


# Scoring Configuration
class ScoringConfig:
    """Configuration for toxicity scoring."""
    MIN_SCORE = 0.0
    MAX_SCORE = 100.0
    DEFAULT_MIN_DURATION = 2  # seconds
    DEFAULT_MAX_DURATION = 15  # seconds


# Retry Configuration
class RetryConfig:
    """Configuration for retry logic."""
    MAX_RETRIES = 3
    INITIAL_DELAY = 1  # seconds
    MAX_DELAY = 60  # seconds
    EXPONENTIAL_BASE = 2


# Validation Messages
class ValidationMessage:
    """Standard validation error messages."""
    INVALID_OPERATION = "Invalid operation type: {operation}"
    SCORE_REQUIRED = "Score must be provided for {operation} operation"
    INVALID_SCORE_RANGE = "Score must be between {min} and {max}"
    MISSING_FIELD = "Required field '{field}' is missing"

