from typing import Dict, Any
from loguru import logger
from etl.models import ConversationRecord
from pydantic import ValidationError


class Transformer:
    """
    Transformer class to convert raw conversation data into validated ConversationRecord objects.
    """

    def __init__(self):
        logger.info("Transformer initialized.")

    def transform(self, raw: Dict[str, Any]) -> ConversationRecord:
        """
        Transform a raw conversation dictionary into a validated ConversationRecord.

        Args:
            raw (Dict[str, Any]): Raw conversation data.

        Returns:
            ConversationRecord: Validated conversation record.

        Raises:
            ValidationError: If the data is invalid.
            ValueError: If required fields are missing or malformed.
        """
        try:
            record = ConversationRecord.from_dict(raw)
            record.validate()
            logger.debug(f"Transformed record: {record.conversation_id}")
            return record
        except ValidationError as ve:
            logger.error(f"Validation error in Transformer: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error transforming record: {e}")
            raise

# Example usage:
# transformer = Transformer()
# conversation_record = transformer.transform(raw_dict)