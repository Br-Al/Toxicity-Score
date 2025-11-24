from configure_logging import get_logger
import random
import time
from models import Comment
from typing import Union
from database.connection import MongoDBConnection


logging = get_logger(__name__)


def simulate_scoring(min_duration: int=2, max_duration: int=15) -> dict:
    """
    Simulate a scoring process that takes a random duration between min_duration and max_duration seconds.
    :param min_duration: minimum duration in seconds (int)
    :param max_duration: maximum duration in seconds (int)
    :return: dict with scoring result
    """
    duration = random.randint(min_duration, max_duration)
    start_time = time.time()
    logging.info(f"Scoring started, will take approximately {duration} seconds.")
    time.sleep(duration)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Scoring completed in {elapsed_time:.2f} seconds.")
    result = {
        "status": "completed",
        "duration_seconds": elapsed_time,
        "score": random.uniform(0, 100)  # Simulated score
    }

    return result

class CommentService:
    def __init__(self):
        self.db_connection = MongoDBConnection()

    def update(self, comment: Comment, score: float) -> Union[Comment, None]:
        """
        Update the score of a comment.
        :param comment: Comment object
        :param score: float score to be assigned
        :return: Updated Comment object
        """
        comment.score = score
        try:
            result = self.db_connection.db.update_one(
                {"_id": comment.id},
                {"$set": {"score": score}}
            )
            if result.modified_count == 1:
                logging.info(f"Comment {comment.id} score updated to {score}.")
                return comment
            else:
                logging.warning(f"Comment {comment.id} score update failed or no change made.")
                return None
        except Exception:
            logging.error(f"Error updating comment {comment.id} score", exc_info=True)
            return None

    def delete(self, comment_id: str) -> bool:
        """
        Delete a comment by its ID.
        :param comment_id: str Comment ID
        :return: bool indicating success or failure
        """
        try:
            result = self.db_connection.db.delete_one({"_id": comment_id})
            if result.deleted_count == 1:
                logging.info(f"Comment {comment_id} deleted successfully.")
                return True
            else:
                logging.warning(f"Comment {comment_id} deletion failed or not found.")
                return False
        except Exception:
            logging.error(f"Error deleting comment {comment_id}", exc_info=True)
            return False


    def add(self, comment: Comment) -> Union[Comment, None]:
        """
        Add a new comment to the database.
        :param comment: Comment object
        :return: Added Comment object with ID
        """
        try:
            result = self.db_connection.db.insert_one(comment.dict(exclude={"id"}))
            comment.id = str(result.inserted_id)
            logging.info(f"Comment added with ID {comment.id}.")
            return comment
        except Exception:
            logging.error("Error adding new comment", exc_info=True)
            return None

    def process_ops(self, comment: Comment, ops: str, score: float=None) -> Union[Comment, bool, None]:
        """
        Process operations on a comment based on the ops parameter.
        :param comment: Comment object
        :param ops: str operation type ("create", "update", "delete")
        :param score: float score to be assigned (for create and update)
        :return: Updated Comment object, bool for delete, or None for failure
        """
        ops = ops.lower()
        if ops == "create":
            return self.add(comment)
        elif ops == "update":
            if score is not None:
                return self.update(comment, score)
            else:
                logging.error("Score must be provided for update operation.")
                return None
        elif ops == "delete":
            return self.delete(comment.id)
        else:
            logging.error(f"Invalid operation type: {ops}")
            return None