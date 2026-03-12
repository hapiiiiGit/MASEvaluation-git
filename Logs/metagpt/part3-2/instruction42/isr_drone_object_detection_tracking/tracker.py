import numpy as np
from typing import List, Tuple, Dict, Any

# Import DeepSORT and ByteTrack dependencies
try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
except ImportError:
    DeepSort = None

try:
    from bytetrack import BYTETracker
except ImportError:
    BYTETracker = None

# Import Detection and define Track (as per class diagram)
class Detection:
    """
    Represents a single object detection result.
    """
    def __init__(self, class_id: int, class_name: str, bbox: Tuple[int, int, int, int], confidence: float):
        self.class_id = class_id
        self.class_name = class_name
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence

class Track:
    """
    Represents a single tracked object.
    """
    def __init__(self, track_id: int, class_id: int, class_name: str, bbox: Tuple[int, int, int, int], confidence: float):
        self.track_id = track_id
        self.class_id = class_id
        self.class_name = class_name
        self.bbox = bbox
        self.confidence = confidence

class DeepSORTTracker:
    """
    DeepSORT-based object tracker.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config (dict): Configuration dictionary for DeepSORT.
        """
        if DeepSort is None:
            raise ImportError("deep_sort_realtime is not installed.")
        self.max_age = config.get("max_age", 30)
        self.n_init = config.get("n_init", 3)
        self.nms_max_overlap = config.get("nms_max_overlap", 1.0)
        self.embedder = config.get("embedder", "mobilenet")
        self.half = config.get("half", True)
        self.budget = config.get("budget", None)
        self.deep_sort = DeepSort(
            max_age=self.max_age,
            n_init=self.n_init,
            nms_max_overlap=self.nms_max_overlap,
            embedder=self.embedder,
            half=self.half,
            budget=self.budget
        )

    def update(self, detections: List[Detection], frame: np.ndarray) -> List[Track]:
        """
        Update tracker with new detections and return active tracks.

        Args:
            detections (List[Detection]): List of Detection objects.
            frame (np.ndarray): Current video frame.

        Returns:
            List[Track]: List of active Track objects.
        """
        # Prepare detections for DeepSORT: [[x1, y1, x2, y2, confidence, class_id], ...]
        dets = []
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            dets.append([x1, y1, x2, y2, det.confidence, det.class_id])

        # DeepSORT expects detections as a numpy array
        if len(dets) == 0:
            dets_np = np.empty((0, 6))
        else:
            dets_np = np.array(dets)

        tracks = []
        outputs = self.deep_sort.update_tracks(dets_np, frame=frame)
        for t in outputs:
            if not t.is_confirmed():
                continue
            track_id = t.track_id
            ltrb = t.to_ltrb()
            class_id = int(t.det_class) if hasattr(t, "det_class") else -1
            class_name = str(class_id)
            confidence = float(t.det_conf) if hasattr(t, "det_conf") else 0.0
            if hasattr(t, "det_class_name"):
                class_name = t.det_class_name
            bbox = (int(ltrb[0]), int(ltrb[1]), int(ltrb[2]), int(ltrb[3]))
            tracks.append(Track(track_id, class_id, class_name, bbox, confidence))
        return tracks

class ByteTrackTracker:
    """
    ByteTrack-based object tracker.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config (dict): Configuration dictionary for ByteTrack.
        """
        if BYTETracker is None:
            raise ImportError("bytetrack is not installed.")
        self.tracker = BYTETracker(
            track_thresh=config.get("track_thresh", 0.5),
            match_thresh=config.get("match_thresh", 0.8),
            track_buffer=config.get("track_buffer", 30),
            frame_rate=config.get("frame_rate", 30),
            min_box_area=config.get("min_box_area", 10)
        )
        self.frame_id = 0

    def update(self, detections: List[Detection], frame: np.ndarray) -> List[Track]:
        """
        Update tracker with new detections and return active tracks.

        Args:
            detections (List[Detection]): List of Detection objects.
            frame (np.ndarray): Current video frame.

        Returns:
            List[Track]: List of active Track objects.
        """
        self.frame_id += 1
        # Prepare detections for ByteTrack: [[x1, y1, x2, y2, score, class_id], ...]
        dets = []
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            dets.append([x1, y1, x2, y2, det.confidence, det.class_id])
        if len(dets) == 0:
            dets_np = np.empty((0, 6), dtype=np.float32)
        else:
            dets_np = np.array(dets, dtype=np.float32)

        # ByteTrack expects detections as numpy array
        online_targets = self.tracker.update(dets_np, frame)
        tracks = []
        for t in online_targets:
            track_id = int(t.track_id)
            x1, y1, x2, y2 = map(int, t.tlbr)
            class_id = int(t.class_id) if hasattr(t, "class_id") else -1
            class_name = str(class_id)
            confidence = float(t.score) if hasattr(t, "score") else 0.0
            if hasattr(t, "class_name"):
                class_name = t.class_name
            bbox = (x1, y1, x2, y2)
            tracks.append(Track(track_id, class_id, class_name, bbox, confidence))
        return tracks