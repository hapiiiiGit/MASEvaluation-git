import os
from typing import List, Tuple, Optional
import numpy as np

try:
    import torch
except ImportError:
    torch = None

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

try:
    import tensorrt as trt
except ImportError:
    trt = None

class Detection:
    """
    Represents a single object detection result.
    """
    def __init__(self, class_id: int, class_name: str, bbox: Tuple[int, int, int, int], confidence: float):
        self.class_id = class_id
        self.class_name = class_name
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence

class YOLOv8Detector:
    """
    YOLOv8-based object detector with optional TensorRT optimization for Jetson Orin NX.
    """
    def __init__(self, model_path: str, use_tensorrt: bool = True):
        """
        Args:
            model_path (str): Path to YOLOv8 model (.pt or .engine).
            use_tensorrt (bool): Whether to use TensorRT optimization.
        """
        self.model_path = model_path
        self.use_tensorrt = use_tensorrt
        self.model = None
        self.class_names = []
        self._is_trt = False
        self.load_model()

    def load_model(self) -> None:
        """
        Loads the YOLOv8 model, optionally with TensorRT optimization.
        """
        if not os.path.isfile(self.model_path):
            raise FileNotFoundError(f"YOLOv8 model file not found: {self.model_path}")

        ext = os.path.splitext(self.model_path)[1].lower()
        if ext == ".engine":
            # TensorRT engine
            if trt is None:
                raise ImportError("TensorRT is not installed.")
            self._is_trt = True
            self.model = self._load_trt_engine(self.model_path)
            # Class names must be provided separately for TensorRT engine
            self.class_names = self._load_class_names_from_txt(self.model_path.replace('.engine', '.names'))
        elif ext == ".pt":
            # PyTorch model
            if YOLO is None:
                raise ImportError("Ultralytics YOLO is not installed.")
            self.model = YOLO(self.model_path)
            self.class_names = self.model.names
        else:
            raise ValueError("Unsupported model format. Use .pt for PyTorch or .engine for TensorRT.")

    def _load_trt_engine(self, engine_path: str):
        """
        Loads a TensorRT engine from file.
        """
        TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
        with open(engine_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
            engine = runtime.deserialize_cuda_engine(f.read())
        return engine

    def _load_class_names_from_txt(self, names_path: str) -> List[str]:
        """
        Loads class names from a .names file.
        """
        if not os.path.isfile(names_path):
            raise FileNotFoundError(f"Class names file not found: {names_path}")
        with open(names_path, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Runs object detection on a frame.

        Args:
            frame (np.ndarray): Input image (BGR).

        Returns:
            List[Detection]: List of Detection objects.
        """
        if self._is_trt:
            return self._detect_trt(frame)
        else:
            return self._detect_pytorch(frame)

    def _detect_pytorch(self, frame: np.ndarray) -> List[Detection]:
        """
        Runs detection using PyTorch YOLOv8.
        """
        results = self.model(frame)
        detections = []
        for r in results:
            if hasattr(r, 'boxes'):
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.class_names[class_id] if class_id < len(self.class_names) else str(class_id)
                    confidence = float(box.conf[0].cpu().numpy())
                    detections.append(Detection(class_id, class_name, (x1, y1, x2, y2), confidence))
        return detections

    def _detect_trt(self, frame: np.ndarray) -> List[Detection]:
        """
        Runs detection using TensorRT engine.
        Note: This is a simplified example. In production, you should use a proper TensorRT inference pipeline.
        """
        # Placeholder: In production, use a proper TensorRT inference pipeline.
        # For demonstration, we raise NotImplementedError.
        raise NotImplementedError("TensorRT inference pipeline must be implemented for .engine models.")
