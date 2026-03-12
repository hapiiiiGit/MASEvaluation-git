import sys
import signal
import argparse
import time

import numpy as np

from config import Config
from camera import CameraHandler
from detector import YOLOv8Detector, Detection
from tracker import DeepSORTTracker, ByteTrackTracker, Track
from metadata import MetadataOutput

def parse_args():
    parser = argparse.ArgumentParser(description="ISR Drone Object Detection & Tracking System")
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file (YAML or JSON)')
    parser.add_argument('--tracker', type=str, choices=['deepsort', 'bytetrack'], default=None,
                        help='Override tracker algorithm (deepsort or bytetrack)')
    parser.add_argument('--camera', type=str, default=None, help='Override camera source')
    parser.add_argument('--model', type=str, default=None, help='Override YOLOv8 model path')
    parser.add_argument('--tensorrt', action='store_true', help='Force TensorRT optimization')
    parser.add_argument('--no-tensorrt', action='store_true', help='Disable TensorRT optimization')
    return parser.parse_args()

class GracefulKiller:
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print("\nReceived termination signal. Shutting down gracefully...")
        self.kill_now = True

def main():
    args = parse_args()
    # Load configuration
    config = Config(args.config)
    cfg = config.as_dict()

    # Camera source
    camera_source = args.camera if args.camera else config.get('camera.source', 0)

    # YOLOv8 model path
    model_path = args.model if args.model else config.get('detector.model_path', 'yolov8n.pt')
    use_tensorrt = config.get('detector.use_tensorrt', False)
    if args.tensorrt:
        use_tensorrt = True
    if args.no_tensorrt:
        use_tensorrt = False

    # Tracker selection
    tracker_type = args.tracker if args.tracker else config.get('tracker.type', 'deepsort')
    tracker_config = config.get('tracker.config', {})

    # Metadata output
    metadata_output = MetadataOutput()

    # Initialize modules
    print(f"Initializing camera: {camera_source}")
    camera = CameraHandler(camera_source)
    print(f"Initializing YOLOv8 detector: {model_path} (TensorRT: {use_tensorrt})")
    detector = YOLOv8Detector(model_path, use_tensorrt=use_tensorrt)
    print(f"Initializing tracker: {tracker_type}")
    if tracker_type == 'deepsort':
        tracker = DeepSORTTracker(tracker_config)
    elif tracker_type == 'bytetrack':
        tracker = ByteTrackTracker(tracker_config)
    else:
        print(f"Unknown tracker type: {tracker_type}")
        sys.exit(1)

    # Start camera
    camera.start()
    print("Camera started. Beginning detection and tracking loop...")

    killer = GracefulKiller()
    frame_count = 0
    start_time = time.time()

    try:
        while not killer.kill_now:
            frame = camera.read_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            # Run detection
            try:
                detections = detector.detect(frame)
            except NotImplementedError as e:
                print(f"Detection error: {e}")
                break
            except Exception as e:
                print(f"Detection error: {e}")
                continue

            # Run tracking
            try:
                tracks = tracker.update(detections, frame)
            except Exception as e:
                print(f"Tracking error: {e}")
                continue

            # Format and send metadata
            metadata = metadata_output.format(tracks)
            metadata_output.send(metadata)

            frame_count += 1
            # Optional: print FPS every 100 frames
            if frame_count % 100 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"[INFO] Processed {frame_count} frames, FPS: {fps:.2f}")

    except Exception as e:
        print(f"Fatal error: {e}")

    finally:
        print("Stopping camera...")
        camera.stop()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()