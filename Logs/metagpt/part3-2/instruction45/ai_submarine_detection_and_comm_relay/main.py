import os
import sys
import time
import numpy as np

from config import Config
from logger import Logger
from detection_engine import DetectionEngine, DetectionResult
from communication_relay import CommunicationRelay

def simulate_sonar_stream(input_size: int) -> np.ndarray:
    """
    Simulate a raw sonar/hydrophone data stream for demonstration.
    In production, replace with actual data acquisition.

    Args:
        input_size (int): Size of the input vector.

    Returns:
        np.ndarray: Simulated sonar/hydrophone data.
    """
    # Simulate normal background noise with occasional submarine-like signals
    base_signal = np.random.normal(0, 1, input_size)
    # Randomly inject a "submarine" signal
    if np.random.rand() < 0.1:
        # Add a distinct pattern
        base_signal += np.random.normal(5, 0.5, input_size)
    return base_signal

def main():
    # Load configuration
    config_file = os.environ.get("AISUB_CONFIG", "config.json")
    if not os.path.exists(config_file):
        # Create a default config if not present
        default_config = {
            "model_path": "submarine_detector.pt",
            "threshold": 0.5,
            "log_path": "system.log",
            "acoustic_signal_threshold": 0.6,
            "rf_signal_threshold": 0.8,
            "min_switch_interval": 2.0,
            "rf_latency": 0.1,
            "rf_reliability": 0.98,
            "acoustic_latency": 0.5,
            "acoustic_reliability": 0.90,
            "input_size": 128,
            "stream_interval": 0.5,  # seconds
            "run_duration": 10,      # seconds
        }
        with open(config_file, "w") as f:
            import json
            json.dump(default_config, f, indent=4)

    config = Config(config_file)

    # Initialize Logger
    log_path = config.get("log_path", "system.log")
    logger = Logger(log_path)

    # Initialize DetectionEngine
    model_path = config.get("model_path", "submarine_detector.pt")
    threshold = config.get("threshold", 0.5)
    input_size = config.get("input_size", 128)

    # If model file does not exist, create a dummy model for demonstration
    if not os.path.exists(model_path):
        import torch
        from detection_engine import SimpleSubmarineDetector
        dummy_model = SimpleSubmarineDetector(input_size)
        checkpoint = {
            "input_size": input_size,
            "model_state_dict": dummy_model.state_dict()
        }
        torch.save(checkpoint, model_path)

    detection_engine = DetectionEngine(model_path, threshold)

    # Initialize CommunicationRelay
    relay = CommunicationRelay(config)

    # System startup log
    logger.log_event({
        "event": "system_start",
        "timestamp": time.time(),
        "details": {
            "config_file": config_file,
            "model_path": model_path,
            "log_path": log_path
        }
    })

    # Real-time data processing loop
    stream_interval = config.get("stream_interval", 0.5)
    run_duration = config.get("run_duration", 10)
    start_time = time.time()
    processed_count = 0

    try:
        while time.time() - start_time < run_duration:
            # Simulate receiving sonar/hydrophone data
            data = simulate_sonar_stream(input_size)

            # Process data with detection engine
            try:
                detection_result: DetectionResult = detection_engine.process_stream(data)
            except Exception as e:
                logger.log_error(e, {"event": "detection_failed"})
                continue

            # Log detection event
            logger.log_event({
                "event": "detection",
                "timestamp": detection_result.timestamp,
                "detected": detection_result.detected,
                "confidence": detection_result.confidence,
                "details": detection_result.details
            })

            # Simulate signal quality (random for demo, replace with real metric)
            signal_quality = np.clip(np.random.normal(0.75, 0.15), 0.0, 1.0)

            # Switch communication link if needed
            link_type = relay.switch_link(signal_quality)
            logger.log_event({
                "event": "link_switch",
                "timestamp": time.time(),
                "signal_quality": signal_quality,
                "link_type": link_type,
                "status": relay.get_status()
            })

            # Prepare data to send (for demo, send detection result as bytes)
            send_data = str({
                "timestamp": detection_result.timestamp,
                "detected": detection_result.detected,
                "confidence": detection_result.confidence
            }).encode("utf-8")

            send_success = relay.send_data(send_data, link_type)
            logger.log_event({
                "event": "data_send",
                "timestamp": time.time(),
                "link_type": link_type,
                "success": send_success,
                "status": relay.get_status()
            })

            processed_count += 1
            time.sleep(stream_interval)

        # System shutdown log
        logger.log_event({
            "event": "system_shutdown",
            "timestamp": time.time(),
            "processed_count": processed_count
        })

    except KeyboardInterrupt:
        logger.log_event({
            "event": "system_interrupted",
            "timestamp": time.time(),
            "processed_count": processed_count
        })
        print("System interrupted by user.")

    except Exception as e:
        logger.log_error(e, {"event": "system_error"})
        print(f"System error: {e}")

    print(f"System run complete. Processed {processed_count} data streams.")
    print(f"Logs written to {log_path}")

if __name__ == "__main__":
    main()