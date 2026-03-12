import os
import threading
import time
from datetime import datetime
from typing import List

import cv2
import numpy as np
from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.video_stream_handler import VideoStreamHandler
from src.inference_engine import InferenceEngine
from src.alert_manager import AlertManager
from src.config import get_config
from src.utils import Alert

# --- FastAPI App Setup ---
app = FastAPI(
    title="AI Surveillance Backend",
    description="Backend API for AI Surveillance System",
    version="1.0.0"
)

# Allow CORS for dashboard frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global State ---
config = get_config()
RTSP_URL = config["rtsp_url"]
MODEL_PATH = config["model_path"]

video_handler = VideoStreamHandler(RTSP_URL)
inference_engine = InferenceEngine(MODEL_PATH)
alert_manager = AlertManager()
ALERT_HISTORY: List[Alert] = []

# --- Background Frame Processing ---
def frame_processing_loop():
    while video_handler.is_open():
        frame = video_handler.read_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        result = inference_engine.predict(frame)
        if result.get("anomaly", False):
            alert = Alert(
                timestamp=datetime.utcnow(),
                type=result.get("type", "anomaly"),
                details=result
            )
            alert_manager.send_alert(alert)
            ALERT_HISTORY.append(alert)
            # Keep only the latest 100 alerts
            if len(ALERT_HISTORY) > 100:
                ALERT_HISTORY.pop(0)
        time.sleep(0.05)  # ~20 FPS processing

# Start background thread for frame processing
processing_thread = threading.Thread(target=frame_processing_loop, daemon=True)
processing_thread.start()

# --- Video Feed Generator ---
def gen_video_stream():
    while True:
        frame = video_handler.read_frame()
        if frame is None:
            continue
        # Encode frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.05)  # ~20 FPS

# --- API Endpoints ---

@app.get("/alerts", response_class=JSONResponse)
async def get_alerts():
    """Return the list of recent alerts."""
    return [
        {
            "timestamp": alert.timestamp.isoformat(),
            "type": alert.type,
            "details": alert.details
        }
        for alert in ALERT_HISTORY
    ]

@app.get("/video_feed")
async def video_feed():
    """Return the live video feed as multipart JPEG stream."""
    return StreamingResponse(
        gen_video_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/metrics", response_class=JSONResponse)
async def get_metrics():
    """Return basic system metrics (e.g., alert count, uptime)."""
    return {
        "alert_count": len(ALERT_HISTORY),
        "uptime_seconds": int(time.time() - config["start_time"])
    }

@app.on_event("shutdown")
def shutdown_event():
    video_handler.release()

# --- Main Entrypoint (for uvicorn) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.web.api:app", host="0.0.0.0", port=8000, reload=True)