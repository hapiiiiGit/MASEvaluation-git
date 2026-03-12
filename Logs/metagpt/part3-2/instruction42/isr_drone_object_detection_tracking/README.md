# ISR Drone Object Detection & Tracking System

## Overview

This project implements a real-time object detection and tracking system for ISR (Intelligence, Surveillance, Reconnaissance) drones, optimized for NVIDIA Jetson Orin NX. It uses YOLOv8 for object detection, DeepSORT or ByteTrack for tracking, integrates with live camera feeds, outputs real-time metadata, and leverages TensorRT for efficient inference.

---

## Features

- **Real-time object detection** using YOLOv8 (PyTorch or TensorRT engine)
- **Object tracking** with DeepSORT or ByteTrack (interchangeable)
- **Live camera feed integration** (OpenCV or GStreamer)
- **Structured real-time metadata output** (object class, position, confidence, tracking ID)
- **Optimized for Jetson Orin NX** (GPU acceleration, TensorRT)
- **Modular design** for easy algorithm swapping and integration

---

## File Structure
```
├── camera.py
├── config.py
├── detector.py
├── main.py
├── metadata.py
├── requirements.txt
├── tracker.py
├── utils.py
├── README.md
└── docs/
    ├── system_design.md
    ├── system_design-sequence-diagram.mermaid
    └── system_design-sequence-diagram.mermaid-class-diagram
```

---

## Installation

1. **Clone the repository**
   ```bash
   git clone <repo_url>
   cd isr_drone_object_detection_tracking
   ```

2. **Install dependencies**
   - On Jetson Orin NX, ensure you have Python 3.8+ and pip installed.
   - Install Python packages:
     ```bash
     pip install -r requirements.txt
     ```
   - For TensorRT, use NVIDIA SDK Manager or JetPack to install the correct version.
   - For PyTorch, use the Jetson-compatible wheel from NVIDIA or official PyTorch for ARM64.

3. **Download YOLOv8 model**
   - Place your YOLOv8 .pt or .engine model in the project directory.
   - (Optional) Place class names file (.names) for TensorRT engine.

---

## Configuration

Edit `config.yaml` or `config.json` to set camera source, model path, tracker type, and other parameters. Example:
```yaml
camera:
  source: 0  # USB camera index or GStreamer pipeline string

detector:
  model_path: yolov8n.pt
  use_tensorrt: false

tracker:
  type: deepsort
  config:
    max_age: 30
    n_init: 3
```

---

## Usage

Run the main program:
```bash
python3 main.py --config config.yaml
```

Optional arguments:
- `--tracker deepsort|bytetrack` : Select tracking algorithm
- `--camera <source>` : Override camera source
- `--model <path>` : Override YOLOv8 model path
- `--tensorrt` : Force TensorRT optimization
- `--no-tensorrt` : Disable TensorRT optimization

---

## Deployment on Jetson Orin NX

- Ensure JetPack and TensorRT are installed and configured.
- Use NVIDIA's PyTorch and TensorRT wheels for best performance.
- For camera feeds, use USB cameras or CSI cameras supported by OpenCV/GStreamer.
- For TensorRT engine, convert YOLOv8 .pt model using NVIDIA tools if needed.

---

## Troubleshooting

- **Camera not detected:** Check camera source and permissions.
- **TensorRT errors:** Ensure correct version and model conversion.
- **Dependency issues:** Use Jetson-compatible wheels and verify Python version.
- **Performance:** Monitor GPU usage and adjust model/tracker parameters.

---

## License

MIT License
