from pymongo import MongoClient
from config import settings
from configure_logging import get_logger

logging = get_logger(__name__)


class MongoDBConnection:

    def __init__(self):
        self.db_name = settings.MONGODB_DB_NAME
        self.client = None
        self.db = None
        self._connect()


    def _connect(self):
        try:
            logging.info("Connecting to MongoDB server...")
            uri = f"mongodb://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_HOST}:{settings.MONGODB_PORT}/{settings.MONGODB_DB_NAME}?authSource=admin"
            if settings.MONGODB_MODE == "atlas":
                uri = self.uri = f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASS}@{settings.MONGODB_HOST}/{self.db_name}?retryWrites=true&w=majority"
            self.client = MongoClient(uri)
            self.db = self.client[self.db_name]
            logging.info("Connected to MongoDB server successfully.")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB server", exc_info=True)

    def _shutdown(self):
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed.")

    def get_collection(self, name):
        return self.db[name]

    def list_collections(self):
        """Return a list of all collection names in the database."""
        try:
            return self.db.list_collection_names()
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []

