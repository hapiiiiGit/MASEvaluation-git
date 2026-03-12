import json
from typing import List, Dict, Any

class Track:
    """
    Represents a single tracked object.
    """
    def __init__(self, track_id: int, class_id: int, class_name: str, bbox, confidence: float):
        self.track_id = track_id
        self.class_id = class_id
        self.class_name = class_name
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence

class MetadataOutput:
    """
    Handles formatting and sending real-time metadata about tracked objects.
    Accepts a list of Track objects and outputs structured metadata for downstream analytics or mission operations.
    """

    def __init__(self):
        pass

    def format(self, tracks: List[Track]) -> Dict[str, Any]:
        """
        Format a list of Track objects into a structured metadata dictionary.

        Args:
            tracks (List[Track]): List of Track objects.

        Returns:
            dict: Structured metadata dictionary.
        """
        metadata = {
            "objects": []
        }
        for track in tracks:
            obj = {
                "track_id": track.track_id,
                "class_id": track.class_id,
                "class_name": track.class_name,
                "bbox": {
                    "x1": int(track.bbox[0]),
                    "y1": int(track.bbox[1]),
                    "x2": int(track.bbox[2]),
                    "y2": int(track.bbox[3])
                },
                "confidence": float(track.confidence)
            }
            metadata["objects"].append(obj)
        return metadata

    def send(self, metadata: Dict[str, Any]) -> None:
        """
        Send the metadata to downstream systems.
        For demonstration, this implementation prints the metadata as a JSON string.
        In production, this could be replaced with network transmission, file logging, etc.

        Args:
            metadata (dict): Structured metadata dictionary.
        """
        # For demonstration, print to stdout
        print(json.dumps(metadata, indent=2, sort_keys=True))