"""
vehicle_diagnostics_api.py

A FastAPI-based Python API to serve a trained vehicle diagnostics model.
Provides endpoints for real-time diagnostics and model outputs.
Includes automatic OpenAPI documentation.

Author: Alex
"""

import os
import joblib
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------
# Model and Data Definitions
# ---------------------------

MODEL_PATH = os.getenv("MODEL_PATH", "vehicle_diagnostics_model.joblib")

class SensorData(BaseModel):
    """
    Schema for incoming sensor data.
    """
    rpm: float = Field(..., description="Engine RPM")
    speed: float = Field(..., description="Vehicle speed in km/h")
    coolant_temp: float = Field(..., description="Coolant temperature in Celsius")
    throttle_pos: float = Field(..., description="Throttle position percentage")
    maf: float = Field(..., description="Mass Air Flow (g/s)")
    intake_pressure: float = Field(..., description="Intake manifold pressure (kPa)")
    o2_voltage: float = Field(..., description="O2 sensor voltage (V)")
    fuel_level: float = Field(..., description="Fuel level percentage")
    dtc_codes: Optional[List[str]] = Field(default=None, description="List of active Diagnostic Trouble Codes (DTCs)")

class DiagnosticsResult(BaseModel):
    """
    Schema for model output.
    """
    fault_detected: bool = Field(..., description="Whether a fault is detected")
    fault_type: Optional[str] = Field(default=None, description="Type of fault detected, if any")
    anomaly_score: float = Field(..., description="Anomaly score (0-1, higher means more anomalous)")
    recommended_action: Optional[str] = Field(default=None, description="Recommended action for the detected fault")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional diagnostic details")

class ModelInfo(BaseModel):
    """
    Schema for model metadata.
    """
    model_name: str
    version: str
    trained_on: str
    features: List[str]
    description: str

# ---------------------------
# Model Loading
# ---------------------------

def load_model(model_path: str):
    """
    Loads the trained model from disk.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    model = joblib.load(model_path)
    return model

try:
    model = load_model(MODEL_PATH)
    model_info = getattr(model, "model_info", None)
except Exception as e:
    model = None
    model_info = None

# ---------------------------
# FastAPI App Initialization
# ---------------------------

app = FastAPI(
    title="Vehicle Diagnostics API",
    description="API for real-time vehicle diagnostics and anomaly detection using a trained AI model.",
    version="1.0.0",
    contact={
        "name": "Vehicle Diagnostics Team",
        "email": "support@vehiclediag.example.com"
    }
)

# Allow CORS for dashboard frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your dashboard domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Utility Functions
# ---------------------------

def preprocess_input(sensor_data: SensorData):
    """
    Converts SensorData to model input format (list or array).
    """
    # The order of features must match the model's training
    features = [
        sensor_data.rpm,
        sensor_data.speed,
        sensor_data.coolant_temp,
        sensor_data.throttle_pos,
        sensor_data.maf,
        sensor_data.intake_pressure,
        sensor_data.o2_voltage,
        sensor_data.fuel_level,
    ]
    # Optionally encode DTC codes if model supports it
    # For simplicity, we ignore DTC codes here
    return [features]

def interpret_model_output(model_output, anomaly_score, dtc_codes=None):
    """
    Interprets the model's output and returns a DiagnosticsResult.
    """
    fault_detected = bool(model_output)
    fault_type = None
    recommended_action = None
    details = {}

    if fault_detected:
        # Example mapping, should be replaced with actual model logic
        fault_type = "Engine Fault"
        recommended_action = "Check engine and consult mechanic."
        if dtc_codes:
            details["dtc_codes"] = dtc_codes
    else:
        fault_type = None
        recommended_action = "No action required."

    return DiagnosticsResult(
        fault_detected=fault_detected,
        fault_type=fault_type,
        anomaly_score=float(anomaly_score),
        recommended_action=recommended_action,
        details=details if details else None
    )

# ---------------------------
# API Endpoints
# ---------------------------

@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint.
    """
    return {"status": "ok", "message": "Vehicle Diagnostics API is running."}

@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
def get_model_info():
    """
    Returns metadata about the loaded diagnostics model.
    """
    if not model_info:
        raise HTTPException(status_code=503, detail="Model info not available.")
    return model_info

@app.post("/diagnostics", response_model=DiagnosticsResult, tags=["Diagnostics"])
def run_diagnostics(sensor_data: SensorData):
    """
    Run diagnostics on provided sensor data.
    Returns fault detection, anomaly score, and recommended action.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    try:
        X = preprocess_input(sensor_data)
        # Predict fault (binary or multiclass)
        model_output = model.predict(X)[0]
        # Predict anomaly score (e.g., probability or decision function)
        if hasattr(model, "predict_proba"):
            anomaly_score = float(model.predict_proba(X)[0][1])
        elif hasattr(model, "decision_function"):
            anomaly_score = float(model.decision_function(X)[0])
        else:
            anomaly_score = float(model_output)
        result = interpret_model_output(model_output, anomaly_score, sensor_data.dtc_codes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference error: {str(e)}")

@app.post("/diagnostics/batch", response_model=List[DiagnosticsResult], tags=["Diagnostics"])
def run_batch_diagnostics(sensor_data_list: List[SensorData]):
    """
    Run diagnostics on a batch of sensor data records.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    results = []
    for sensor_data in sensor_data_list:
        try:
            X = preprocess_input(sensor_data)
            model_output = model.predict(X)[0]
            if hasattr(model, "predict_proba"):
                anomaly_score = float(model.predict_proba(X)[0][1])
            elif hasattr(model, "decision_function"):
                anomaly_score = float(model.decision_function(X)[0])
            else:
                anomaly_score = float(model_output)
            result = interpret_model_output(model_output, anomaly_score, sensor_data.dtc_codes)
            results.append(result)
        except Exception as e:
            results.append(DiagnosticsResult(
                fault_detected=False,
                fault_type=None,
                anomaly_score=0.0,
                recommended_action=f"Error: {str(e)}",
                details=None
            ))
    return results

# ---------------------------
# Run with: uvicorn vehicle_diagnostics_api:app --reload
# ---------------------------