"""
Unit tests for database connection handling.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from database.connection import MongoDBConnection


class TestMongoDBConnection(unittest.TestCase):
    """Test cases for the MongoDBConnection class."""

    @patch('database.connection.MongoClient')
    @patch('database.connection.settings')
    def test_mongodb_connection_initialization(self, mock_settings, mock_mongo_client):
        """Test MongoDBConnection initialization."""
        mock_settings.MONGODB_DB_NAME = "test_db"
        mock_settings.MONGODB_USER = "user"
        mock_settings.MONGODB_PASSWORD = "pass"
        mock_settings.MONGODB_HOST = "localhost"
        mock_settings.MONGODB_PORT = 27017
        mock_settings.MONGODB_MODE = "local"

        mock_client = MagicMock()
        mock_db = Mock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client

        connection = MongoDBConnection()

        self.assertEqual(connection.db_name, "test_db")
        self.assertIsNotNone(connection.client)
        self.assertIsNotNone(connection.db)

    @patch('database.connection.MongoClient')
    @patch('database.connection.settings')
    def test_mongodb_local_connection_uri(self, mock_settings, mock_mongo_client):
        """Test that local mode generates correct URI."""
        mock_settings.MONGODB_DB_NAME = "test_db"
        mock_settings.MONGODB_USER = "user"
        mock_settings.MONGODB_PASSWORD = "pass123"
        mock_settings.MONGODB_HOST = "localhost"
        mock_settings.MONGODB_PORT = 27017
        mock_settings.MONGODB_MODE = "local"

        mock_client = Mock()
        mock_mongo_client.return_value = mock_client

        connection = MongoDBConnection()

        expected_uri = "mongodb://user:pass123@localhost:27017/test_db?authSource=admin"
        mock_mongo_client.assert_called_once_with(expected_uri)

    @patch('database.connection.MongoClient')
    @patch('database.connection.settings')
    def test_mongodb_atlas_connection_uri(self, mock_settings, mock_mongo_client):
        """Test that atlas mode generates correct URI."""
        mock_settings.MONGODB_DB_NAME = "test_db"
        mock_settings.MONGODB_USER = "atlas_user"
        mock_settings.MONGODB_PASS = "atlas_pass"
        mock_settings.MONGODB_HOST = "cluster.mongodb.net"
        mock_settings.MONGODB_MODE = "atlas"

        mock_client = Mock()
        mock_mongo_client.return_value = mock_client

        connection = MongoDBConnection()

        # Verify atlas URI is used
        call_args = mock_mongo_client.call_args[0][0]
        self.assertIn("mongodb+srv://", call_args)
        self.assertIn("atlas_user", call_args)
        self.assertIn("cluster.mongodb.net", call_args)

    @patch('database.connection.MongoClient')
    @patch('database.connection.settings')
    def test_get_collection(self, mock_settings, mock_mongo_client):
        """Test getting a collection from the database."""
        mock_settings.MONGODB_DB_NAME = "test_db"
        mock_settings.MONGODB_USER = "user"
        mock_settings.MONGODB_PASSWORD = "pass"
        mock_settings.MONGODB_HOST = "localhost"
        mock_settings.MONGODB_PORT = 27017
        mock_settings.MONGODB_MODE = "local"

        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client

        connection = MongoDBConnection()
        collection = connection.get_collection("test_collection")

        self.assertIsNotNone(collection)

    @patch('database.connection.MongoClient')
    @patch('database.connection.settings')
    def test_list_collections(self, mock_settings, mock_mongo_client):
        """Test listing collections from the database."""
        mock_settings.MONGODB_DB_NAME = "test_db"
        mock_settings.MONGODB_USER = "user"
        mock_settings.MONGODB_PASSWORD = "pass"
        mock_settings.MONGODB_HOST = "localhost"
        mock_settings.MONGODB_PORT = 27017
        mock_settings.MONGODB_MODE = "local"

        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["collection1", "collection2"]
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client

        connection = MongoDBConnection()
        collections = connection.list_collections()

        self.assertEqual(len(collections), 2)
        self.assertIn("collection1", collections)
        self.assertIn("collection2", collections)

    @patch('database.connection.MongoClient')
    @patch('database.connection.settings')
    def test_list_collections_error(self, mock_settings, mock_mongo_client):
        """Test list_collections when an error occurs."""
        mock_settings.MONGODB_DB_NAME = "test_db"
        mock_settings.MONGODB_USER = "user"
        mock_settings.MONGODB_PASSWORD = "pass"
        mock_settings.MONGODB_HOST = "localhost"
        mock_settings.MONGODB_PORT = 27017
        mock_settings.MONGODB_MODE = "local"

        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_db.list_collection_names.side_effect = Exception("Connection error")
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client

        connection = MongoDBConnection()
        collections = connection.list_collections()

        self.assertEqual(collections, [])



if __name__ == '__main__':
    unittest.main()

