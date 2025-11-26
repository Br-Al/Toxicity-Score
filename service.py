from configure_logging import get_logger
from models import Comment
from typing import Union
from constants import CollectionName, OperationType, ValidationMessage, QueueName
from database.connection import mongo_connection
logging = get_logger(__name__)


class CommentService:
    """Service for managing comment operations with MongoDB."""

    _index_created = False

    def __init__(self):
        self.collection = mongo_connection.get_collection(CollectionName.COMMENTS)
        # Only create index once per application lifecycle
        if not CommentService._index_created:
            try:
                self.collection.create_index("id", unique=True)
                CommentService._index_created = True
                logging.debug("Created unique index on 'id' field")
            except Exception as e:
                # Index might already exist, that's okay
                logging.debug("Index creation skipped (may already exist)", exc_info=True)

    def update(self, comment: Comment, score: float) -> Union[Comment, None]:
        """
        Update the score of a comment.
        :param comment: Comment object
        :param score: float score to be assigned
        :return: Updated Comment object
        """
        comment.score = score
        try:
            result = self.collection.update_one(
                {"id": comment.id},
                {"$set": {"score": score}}
            )
            if result.modified_count == 1:
                logging.info(f"Comment {comment.id} score updated to {score}.")
                return comment
            else:
                logging.warning(f"Comment {comment.id} score update failed or no change made.")
                return None
        except Exception as e:
            logging.error(f"Error updating comment {comment.id} score", exc_info=True)
            raise e

    def delete(self, comment_id: str) -> bool:
        """
        Delete a comment by its ID.
        :param comment_id: str Comment ID
        :return: bool indicating success or failure
        """
        try:
            result = self.collection.delete_one({"id": comment_id})
            if result.deleted_count == 1:
                logging.info(f"Comment {comment_id} deleted successfully.")
                return True
            else:
                logging.warning(f"Comment {comment_id} deletion failed or not found.")
                return False
        except Exception as e:
            logging.error(f"Error deleting comment {comment_id}", exc_info=True)
            raise e


    def add(self, comment: Comment) -> Union[Comment, None]:
        """
        Add a new comment to the database.
        :param comment: Comment object
        :return: Added Comment object with ID
        """
        try:
            result = self.collection.insert_one(comment.__dict__)
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
        if ops == OperationType.CREATE:
            return self.add(comment)
        elif ops == OperationType.UPDATE:
            if score is not None:
                return self.update(comment, score)
            else:
                logging.error(ValidationMessage.SCORE_REQUIRED.format(operation="update"))
                return None
        elif ops == OperationType.DELETE:
            return self.delete(comment.id)
        else:
            logging.error(ValidationMessage.INVALID_OPERATION.format(operation=ops))
            return None
