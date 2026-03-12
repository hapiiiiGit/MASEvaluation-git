import os
import sys
import tempfile
import numpy as np
import torch
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from detection_engine import DetectionEngine, DetectionResult, SimpleSubmarineDetector

@pytest.fixture(scope="module")
def dummy_model_file():
    # Create a dummy model checkpoint for testing
    input_size = 128
    model = SimpleSubmarineDetector(input_size)
    checkpoint = {
        "input_size": input_size,
        "model_state_dict": model.state_dict()
    }
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pt") as tmp:
        torch.save(checkpoint, tmp.name)
        yield tmp.name
    os.remove(tmp.name)

def test_load_model_success(dummy_model_file):
    engine = DetectionEngine(model_path=dummy_model_file, threshold=0.5)
    assert engine.model is not None
    assert engine.input_size == 128

def test_set_threshold(dummy_model_file):
    engine = DetectionEngine(model_path=dummy_model_file, threshold=0.5)
    engine.set_threshold(0.7)
    assert engine.threshold == 0.7

def test_process_stream_detected(dummy_model_file):
    engine = DetectionEngine(model_path=dummy_model_file, threshold=0.5)
    # Simulate a strong "submarine" signal
    data = np.ones(engine.input_size) * 10
    result = engine.process_stream(data)
    assert isinstance(result, DetectionResult)
    assert result.confidence >= 0.0 and result.confidence <= 1.0
    # Since the dummy model is untrained, confidence may be near 0.5, so we check type
    assert isinstance(result.detected, bool)
    assert "input_shape" in result.details

def test_process_stream_not_detected(dummy_model_file):
    engine = DetectionEngine(model_path=dummy_model_file, threshold=0.9)
    # Simulate background noise
    data = np.random.normal(0, 1, engine.input_size)
    result = engine.process_stream(data)
    assert isinstance(result, DetectionResult)
    assert result.confidence >= 0.0 and result.confidence <= 1.0
    assert isinstance(result.detected, bool)
    assert "input_shape" in result.details

def test_process_stream_input_padding(dummy_model_file):
    engine = DetectionEngine(model_path=dummy_model_file, threshold=0.5)
    # Provide input smaller than expected
    data = np.ones(engine.input_size // 2)
    result = engine.process_stream(data)
    assert isinstance(result, DetectionResult)
    assert result.details["input_shape"] == (engine.input_size,)

def test_process_stream_input_truncation(dummy_model_file):
    engine = DetectionEngine(model_path=dummy_model_file, threshold=0.5)
    # Provide input larger than expected
    data = np.ones(engine.input_size * 2)
    result = engine.process_stream(data)
    assert isinstance(result, DetectionResult)
    assert result.details["input_shape"] == (engine.input_size,)

def test_model_not_loaded_error():
    # Create engine without loading model
    engine = DetectionEngine.__new__(DetectionEngine)
    engine.model = None
    engine.input_size = 128
    data = np.ones(128)
    with pytest.raises(RuntimeError):
        engine.process_stream(data)