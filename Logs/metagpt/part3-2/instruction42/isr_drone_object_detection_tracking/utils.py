import logging
import os
import sys
import cv2
import numpy as np
from typing import Tuple, Optional, Any


def setup_logger(name: str = "isr_drone", level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level.

    Args:
        name (str): Logger name.
        level (int): Logging level.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def ensure_dir(path: str) -> None:
    """
    Ensure that a directory exists.

    Args:
        path (str): Directory path.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def resize_with_aspect_ratio(
    image: np.ndarray, 
    width: Optional[int] = None, 
    height: Optional[int] = None, 
    inter=cv2.INTER_AREA
) -> np.ndarray:
    """
    Resize an image while maintaining aspect ratio.

    Args:
        image (np.ndarray): Input image.
        width (int, optional): Desired width.
        height (int, optional): Desired height.
        inter: Interpolation method.

    Returns:
        np.ndarray: Resized image.
    """
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    return cv2.resize(image, dim, interpolation=inter)


def letterbox(
    image: np.ndarray, 
    new_shape: Tuple[int, int] = (640, 640), 
    color: Tuple[int, int, int] = (114, 114, 114)
) -> np.ndarray:
    """
    Resize image and pad to meet new_shape, maintaining aspect ratio.

    Args:
        image (np.ndarray): Input image.
        new_shape (tuple): Desired shape (width, height).
        color (tuple): Padding color.

    Returns:
        np.ndarray: Letterboxed image.
    """
    shape = image.shape[:2]  # current shape [height, width]
    ratio = min(new_shape[0] / shape[1], new_shape[1] / shape[0])
    new_unpad = (int(round(shape[1] * ratio)), int(round(shape[0] * ratio)))
    dw = new_shape[0] - new_unpad[0]
    dh = new_shape[1] - new_unpad[1]
    dw /= 2
    dh /= 2

    img = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img


def draw_bboxes(
    image: np.ndarray, 
    bboxes: list, 
    labels: Optional[list] = None, 
    colors: Optional[list] = None, 
    thickness: int = 2
) -> np.ndarray:
    """
    Draw bounding boxes on an image.

    Args:
        image (np.ndarray): Input image.
        bboxes (list): List of bounding boxes [(x1, y1, x2, y2), ...].
        labels (list, optional): List of labels for each bbox.
        colors (list, optional): List of colors for each bbox.
        thickness (int): Line thickness.

    Returns:
        np.ndarray: Image with bounding boxes.
    """
    img = image.copy()
    for i, bbox in enumerate(bboxes):
        color = colors[i] if colors and i < len(colors) else (0, 255, 0)
        x1, y1, x2, y2 = bbox
        cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
        if labels and i < len(labels):
            label = labels[i]
            cv2.putText(
                img, str(label), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, color, 2, cv2.LINE_AA
            )
    return img


def safe_cast(val: Any, to_type: type, default: Any = None) -> Any:
    """
    Safely cast a value to a given type.

    Args:
        val (Any): Value to cast.
        to_type (type): Type to cast to.
        default (Any): Default value if cast fails.

    Returns:
        Any: Casted value or default.
    """
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def get_device() -> str:
    """
    Get the best available device for inference.

    Returns:
        str: 'cuda' if available, else 'cpu'
    """
    try:
        import torch
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    except ImportError:
        return 'cpu'