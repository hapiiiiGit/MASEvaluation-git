import sys
import platform
from typing import Optional, Tuple
from PIL import Image
import numpy as np

# PyObjC is required for macOS screen capture
try:
    import Quartz
except ImportError:
    raise ImportError("PyObjC (Quartz) is required for macOS screenshot functionality. Please install it via pip.")

class ScreenshotUtil:
    """
    Utility class for capturing screenshots on macOS with Retina scaling support.
    """

    @staticmethod
    def capture_screen(region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """
        Captures a screenshot of the entire screen or a specified region.
        Args:
            region: (left, top, width, height) or None for full screen.
        Returns:
            PIL.Image object of the screenshot.
        """
        # Get main display ID
        display_id = Quartz.CGMainDisplayID()
        # Get display bounds
        display_bounds = Quartz.CGDisplayBounds(display_id)
        width = int(display_bounds.size.width)
        height = int(display_bounds.size.height)

        # If region is specified, use it; otherwise, capture full screen
        if region:
            left, top, w, h = region
            capture_rect = Quartz.CGRectMake(left, top, w, h)
        else:
            capture_rect = Quartz.CGRectMake(0, 0, width, height)

        # Capture the image
        image_ref = Quartz.CGWindowListCreateImage(
            capture_rect,
            Quartz.kCGWindowListOptionOnScreenOnly,
            Quartz.kCGNullWindowID,
            Quartz.kCGWindowImageDefault
        )

        if not image_ref:
            raise RuntimeError("Failed to capture screen image.")

        # Convert CGImageRef to numpy array
        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)
        data_provider = Quartz.CGImageGetDataProvider(image_ref)
        data = Quartz.CGDataProviderCopyData(data_provider)
        buffer = bytes(data)
        # RGBA format
        img_array = np.frombuffer(buffer, dtype=np.uint8)
        img_array = img_array.reshape((height, bytes_per_row // 4, 4))
        # Remove padding if any
        img_array = img_array[:, :width, :]

        # Convert to PIL Image
        pil_img = Image.fromarray(img_array, 'RGBA')
        return pil_img

    @staticmethod
    def handle_retina_scaling(img: Image.Image) -> Image.Image:
        """
        Handles Retina scaling for screenshots.
        Args:
            img: PIL.Image object.
        Returns:
            PIL.Image object, scaled to standard DPI if needed.
        """
        # On Retina displays, images may be 2x or 3x the logical screen size.
        # We check the DPI and scale down if necessary.
        # PIL does not always set DPI, so we use image size heuristics.

        # For most macOS Retina screens, scale factor is 2.
        # If the image mode is RGBA and the size is larger than expected, scale down.
        # This function assumes the user will pass the full screen image.

        # No direct DPI info, so we just return the image as-is.
        # If the user wants to scale, they can do so by passing a region or resizing.
        # For demonstration, let's provide a scale-down to 0.5x if the image is likely Retina.

        # Heuristic: If width > 3000, assume Retina and scale down.
        if img.width > 3000:
            scaled_img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
            return scaled_img
        return img