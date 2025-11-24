from pymongo import MongoClient
from config import settings
from configure_logging import get_logger

logging = get_logger(__name__)


class MongoDBConnection:

    def __init__(self):
        self.atlas_uri = f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_HOST}/{settings.MONGODB_DB_NAME}?retryWrites=true&w=majority"
        self.db_name = settings.MONGODB_DB_NAME
        self.client = None
        self.db = None
        self._connect()


    def _connect(self):
        try:
            logging.info("Connecting to MongoDB server...")
            self.client = MongoClient(self.atlas_uri)
            self.db = self.client[self.db_name]
            logging.info("Connected to MongoDB server successfully.")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB server", exc_info=True)

    def _shutdown(self):
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed.")
