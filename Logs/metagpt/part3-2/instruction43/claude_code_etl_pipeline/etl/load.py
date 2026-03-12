from typing import List
from loguru import logger
from etl.models import ConversationRecord
import questdb
from questdb.ingress import Sender, IngressError
import threading
import time


class Loader:
    """
    Loader class for atomic, idempotent inserts into QuestDB.
    Supports single and bulk insert operations with error handling.
    """

    def __init__(self, db_uri: str):
        """
        Initialize the Loader.

        Args:
            db_uri (str): QuestDB connection URI, e.g., 'localhost:9009'.
        """
        self.db_uri = db_uri
        self._parse_db_uri()
        self.lock = threading.Lock()
        logger.info(f"Loader initialized for QuestDB at {self.host}:{self.port}")

    def _parse_db_uri(self):
        """
        Parse the db_uri into host and port.
        """
        if "://" in self.db_uri:
            # Remove protocol if present
            self.db_uri = self.db_uri.split("://", 1)[1]
        parts = self.db_uri.split(":")
        if len(parts) != 2:
            raise ValueError("db_uri must be in format 'host:port'")
        self.host = parts[0]
        self.port = int(parts[1])

    def _get_sender(self):
        """
        Create a QuestDB Sender instance.
        """
        try:
            sender = Sender(self.host, self.port)
            return sender
        except Exception as e:
            logger.error(f"Failed to create QuestDB sender: {e}")
            raise

    def insert(self, record: ConversationRecord) -> bool:
        """
        Insert a single ConversationRecord into QuestDB atomically and idempotently.

        Args:
            record (ConversationRecord): The record to insert.

        Returns:
            bool: True if insert succeeded, False otherwise.
        """
        with self.lock:
            try:
                sender = self._get_sender()
                # Prepare line protocol string
                line = self._record_to_line_protocol(record)
                sender.data(line)
                sender.flush()
                sender.close()
                logger.info(f"Inserted record {record.conversation_id} into QuestDB.")
                return True
            except IngressError as ie:
                logger.error(f"QuestDB ingress error: {ie}")
                return False
            except Exception as e:
                logger.error(f"Failed to insert record {record.conversation_id}: {e}")
                return False

    def bulk_insert(self, records: List[ConversationRecord]) -> bool:
        """
        Bulk insert ConversationRecords into QuestDB atomically and idempotently.

        Args:
            records (List[ConversationRecord]): List of records to insert.

        Returns:
            bool: True if all inserts succeeded, False otherwise.
        """
        if not records:
            logger.warning("No records provided for bulk insert.")
            return True

        with self.lock:
            try:
                sender = self._get_sender()
                for record in records:
                    line = self._record_to_line_protocol(record)
                    sender.data(line)
                sender.flush()
                sender.close()
                logger.info(f"Bulk inserted {len(records)} records into QuestDB.")
                return True
            except IngressError as ie:
                logger.error(f"QuestDB ingress error during bulk insert: {ie}")
                return False
            except Exception as e:
                logger.error(f"Failed bulk insert: {e}")
                return False

    def _record_to_line_protocol(self, record: ConversationRecord) -> str:
        """
        Convert a ConversationRecord to QuestDB line protocol string.

        Args:
            record (ConversationRecord): The record to convert.

        Returns:
            str: Line protocol string.
        """
        # Table name: conversations
        # Tags: conversation_id, user_id
        # Fields: messages (as JSON string)
        # Timestamp: timestamp (in nanoseconds)
        import json

        # QuestDB expects nanoseconds since epoch
        ts_ns = int(record.timestamp.timestamp() * 1e9)
        messages_json = json.dumps(record.messages).replace('"', '\\"')
        line = (
            f"conversations,"
            f"conversation_id={record.conversation_id},"
            f"user_id={record.user_id} "
            f"messages=\"{messages_json}\" "
            f"{ts_ns}"
        )
        return line

# Example usage:
# loader = Loader("localhost:9009")
# success = loader.insert(conversation_record)
# bulk_success = loader.bulk_insert([conversation_record1, conversation_record2])