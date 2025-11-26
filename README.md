# Toxicity-Score

A Python-based message processing system that simulates toxicity scoring for text comments using RabbitMQ for message queuing and MongoDB for data persistence.

## Table of Contents

- [Quick Start](#quick-start)
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Testing](#testing)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Quick Start

For those who want to get up and running quickly:

```cmd
# 1. Clone the repository
git clone https://github.com/yourusername/Toxicity-Score.git
cd Toxicity-Score

# 2. Start Docker containers
docker-compose up -d

# 3. Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 4. Copy and configure environment file
copy .env.exemple .env

# 5. Run the application
python main.py
```

Visit http://localhost:15672 for RabbitMQ Management UI (guest/guest)

## Overview

This project implements a message-driven architecture for processing text comments and assigning toxicity scores. It uses:
- **RabbitMQ** for asynchronous message handling
- **MongoDB** for storing comments and their scores
- **Pydantic** for data validation
- **Structlog** for structured logging

## Features

- 🔄 Asynchronous message processing with RabbitMQ
- 📊 Simulated toxicity scoring (2-15 seconds processing time)
- 💾 MongoDB integration for data persistence
- 🔍 Support for CRUD operations (Create, Update, Delete)
- 📝 Structured logging with JSON and console output
- ⚙️ Configurable via environment variables
- 🐳 Docker support for easy setup and deployment

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Docker Desktop** - [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
- **Git** (optional) - For cloning the repository

### Installing Docker Desktop (Windows)

1. Download Docker Desktop from [Docker Downloads](https://www.docker.com/products/docker-desktop/)
2. Run the installer and follow the setup wizard
3. Restart your computer if prompted
4. Launch Docker Desktop and wait for it to start
5. Verify installation:
   ```cmd
   docker --version
   docker-compose --version
   ```

### Setting up RabbitMQ with Docker

Run the RabbitMQ container with management plugin enabled:

```cmd
docker run -d --name rabbitmq ^
  -p 5672:5672 ^
  -p 15672:15672 ^
  -e RABBITMQ_DEFAULT_USER=guest ^
  -e RABBITMQ_DEFAULT_PASS=guest ^
  rabbitmq:3-management
```

Access RabbitMQ Management UI at http://localhost:15672 (default credentials: guest/guest)

### Setting up MongoDB with Docker

Run the MongoDB container:

```cmd
docker run -d --name mongodb ^
  -p 27017:27017 ^
  -e MONGO_INITDB_ROOT_USERNAME=user ^
  -e MONGO_INITDB_ROOT_PASSWORD=password ^
  mongo:latest
```

### Alternative: Using Docker Compose (Recommended)

For easier management, you can use Docker Compose. Create a `docker-compose.yml` file:


## Installation

### 1. Clone the Repository

```cmd
git clone https://github.com/yourusername/Toxicity-Score.git
cd Toxicity-Score
```

### 2. Create a Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```cmd
pip install -r requirements.txt
```

## Configuration

### 1. Create Environment File

Copy the example environment file and configure it:

```cmd
copy .env.exemple .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your settings:

```dotenv
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# RabbitMQ Exchange and Queue Settings
RABBITMQ_CONSUMER_QUEUE=incoming_texts
RABBITMQ_CONSUMER_EXCHANGE=ex.toxicity.service
RABBITMQ_CONSUMER_EXCHANGE_TYPE=topic
RABBITMQ_CONSUMER_ROUTING_KEY=event.request.text.#
RABBITMQ_PUBLISHER_EXCHANGE=ex.toxicity.service
RABBITMQ_PUBLISHER_ROUTING_KEY=event.request.text
RABBITMQ_PUBLISHER_QUEUE=processed_texts

# Application Settings
PUBLISH_SAMPLE_MESSAGES=True
RABBITMQ_START_CONSUMING=True
SAMPLE_MESSAGES_COUNT=10
LOG_LEVEL=DEBUG

# MongoDB Configuration
MONGODB_USER=user
MONGODB_PASSWORD=password
MONGODB_DB_NAME=toxicity_score
MONGODB_HOST=localhost
MONGODB_PORT=27017
```

### 3. Setup MongoDB User

Connect to MongoDB and create a user:

```cmd
mongosh
```

Then run:

```javascript
use admin
db.createUser({
  user: "user",
  pwd: "password",
  roles: [{ role: "readWrite", db: "toxicity_score" }]
})
```

## Usage

### Running the Application

Activate your virtual environment and run:

```cmd
venv\Scripts\activate
python main.py
```

### Running Modes

The application can run in different modes based on environment variables:

#### 1. Publisher + Consumer Mode (Default)
```dotenv
PUBLISH_SAMPLE_MESSAGES=True
RABBITMQ_START_CONSUMING=True
```
This will:
- Publish sample messages to RabbitMQ
- Start consuming and processing messages

#### 2. Consumer Only Mode
```dotenv
PUBLISH_SAMPLE_MESSAGES=False
RABBITMQ_START_CONSUMING=True
```
Only consumes messages from the queue.

#### 3. Publisher Only Mode
```dotenv
PUBLISH_SAMPLE_MESSAGES=True
RABBITMQ_START_CONSUMING=False
```
Only publishes sample messages to the queue.

### Monitoring

1. **RabbitMQ Management UI**: http://localhost:15672
   - View queues, exchanges, and message rates
   - Monitor connections and channels

2. **Logs**: Check the `logs/app.log` file for detailed JSON logs

3. **MongoDB**: Use MongoDB Compass or mongosh to view stored comments

## Project Structure

```
Toxicity-Score/
├── config.py                    # Configuration settings using Pydantic
├── configure_logging.py         # Logging configuration with structlog
├── main.py                      # Application entry point
├── models.py                    # Pydantic models (Comment, Message)
├── utils.py                     # Utility functions and CommentService
├── constants.py                 # NEW: Centralized constants and enums
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Docker services configuration
├── pyproject.toml               # Pytest configuration
├── pytest.ini                   # Alternative pytest configuration
├── .env                         # Environment variables (not in git)
├── .env.exemple                 # Example environment file
├── database/
│   ├── __init__.py
│   └── connection.py            # MongoDB connection handler
├── rabbitmq/
│   ├── __init__.py
│   ├── connection.py            # RabbitMQ connection handler
│   ├── consumers/
│   │   ├── __init__.py
│   │   └── message_consumer.py  # Message consumer implementation
│   └── publishers/
│       ├── __init__.py
│       └── message_publisher.py # Message publisher implementation
├── tests/
│   ├── __init__.py
│   ├── run_tests.py             # Test runner script
│   ├── test_models.py           # Unit tests for models
│   ├── test_utils.py            # Unit tests for utilities
│   ├── test_config.py           # Unit tests for configuration
│   ├── test_database.py         # Unit tests for database
│   ├── test_rabbitmq.py         # Unit tests for RabbitMQ
│   └── TESTING.md               # Testing documentation
└── logs/
    └── app.log                  # Application logs (JSON format)
```

## How It Works

### Message Flow

1. **Publisher Process**:
   - Generates sample messages with random text and metadata
   - Publishes messages to RabbitMQ exchange with routing key pattern
   - Each message includes: id, user_id, text, timestamp, and type (create/update/delete)

2. **Consumer Process**:
   - Listens to the RabbitMQ queue
   - Receives messages and processes them based on operation type:
     - **CREATE**: Adds new comment to MongoDB with toxicity score
     - **UPDATE**: Updates existing comment's toxicity score
     - **DELETE**: Removes comment from MongoDB
   - Simulates scoring process (2-15 seconds)
   - Publishes processing result back to RabbitMQ

3. **Database Storage**:
   - Comments are stored in MongoDB with scores
   - Unique index on comment ID prevents duplicates
   - Timestamps track creation, update, and deletion

### Message Format

**Incoming Message**:
```json
{
  "id": "msg_1",
  "user_id": "u_1234",
  "text": "Sample comment text",
  "timestamp": "2025-11-25T10:00:00",
  "type": "create"
}
```

**Result Message**:
```json
{
  "_id": "uuid",
  "type": "create",
  "status": "processed",
  "message_id": "msg_1",
  "processed_at": "2025-11-25T10:00:15"
}
```

## Testing

The project includes a comprehensive unit test suite with **65 test cases** covering all major components.

### Quick Test Commands

**Run all tests:**
```cmd
python -m unittest discover tests
```

**Run with pytest:**
```cmd
pytest
```

**Run specific test file:**
```cmd
python -m unittest tests.test_models
```


### Running Tests

The project includes a comprehensive unit test suite. Testing dependencies are included in `requirements.txt`.

**Run all tests:**
```cmd
pytest
```

**Run specific test file:**
```cmd
pytest tests/test_models.py
```

**Using the test runner:**
```cmd
python tests\run_tests.py
```

### Code Style

The project follows Python best practices:
- Type hints for function parameters
- Pydantic models for data validation
- Structured logging with context
- Error handling with retries
- Comprehensive unit tests with >80% coverage
- Mocking external dependencies in tests

## Troubleshooting

### RabbitMQ Connection Issues

**Problem**: `Failed to connect to RabbitMQ server`

**Solutions**:
- Verify RabbitMQ service is running: `rabbitmq-server`
- Check credentials in `.env` file
- Ensure port 5672 is not blocked by firewall
- Check RabbitMQ logs: `C:\Program Files\RabbitMQ Server\rabbitmq_server-x.x.x\`

### MongoDB Connection Issues

**Problem**: `Failed to connect to MongoDB server`

**Solutions**:
- Verify MongoDB service is running: `net start MongoDB`
- Check credentials match those created in MongoDB
- Ensure MongoDB is listening on port 27017
- Try connection without auth first: Set `MONGODB_USER` and `MONGODB_PASSWORD` to empty

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solutions**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11+)

### Message Not Processing

**Problem**: Messages stuck in queue

**Solutions**:
- Check RabbitMQ settings
- Verify consumer is running: Check logs
- Check for exceptions in `logs/app.log`
- Inspect message format matches expected schema

### Logs Not Appearing

**Problem**: No logs in `logs/app.log`

**Solutions**:
- Check `LOGGING_PATH` directory exists
- Verify write permissions on logs directory
- Check `LOG_LEVEL` setting in `.env`

## License

This project is for testing and educational purposes


## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review logs in `logs/app.log`
