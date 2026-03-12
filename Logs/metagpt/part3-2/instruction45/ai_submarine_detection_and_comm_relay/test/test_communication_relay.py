import pytest
import time
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from communication_relay import CommunicationRelay

class DummyConfig:
    def __init__(self):
        self._config = {
            "acoustic_signal_threshold": 0.6,
            "rf_signal_threshold": 0.8,
            "min_switch_interval": 0.1,
            "rf_latency": 0.01,
            "rf_reliability": 1.0,  # For deterministic test
            "acoustic_latency": 0.02,
            "acoustic_reliability": 1.0,  # For deterministic test
        }
    def get(self, key, default=None):
        return self._config.get(key, default)

@pytest.fixture
def relay():
    return CommunicationRelay(DummyConfig())

def test_initial_status(relay):
    assert relay.get_status() == "initialized"
    assert relay.link_type == "acoustic"

def test_switch_link_rf(relay):
    # Should switch to RF if signal quality is high
    link = relay.switch_link(0.85)
    assert link == "rf"
    assert "Switched from acoustic to rf" in relay.get_status()

def test_switch_link_acoustic(relay):
    # Should switch to acoustic if signal quality is moderate
    relay.switch_link(0.85)  # First switch to RF
    time.sleep(0.11)         # Wait for min_switch_interval
    link = relay.switch_link(0.65)
    assert link == "acoustic"
    assert "Switched from rf to acoustic" in relay.get_status()

def test_switch_link_no_switch(relay):
    # Should not switch if called within min_switch_interval
    relay.switch_link(0.85)  # Switch to RF
    link = relay.switch_link(0.85)  # Immediate call, should not switch
    assert link == "rf"
    assert "No switch. Link remains rf." in relay.get_status()

def test_switch_link_poor_signal(relay):
    # Should default to acoustic if signal is poor
    time.sleep(0.11)
    link = relay.switch_link(0.2)
    assert link == "acoustic"
    assert "Link remains acoustic" in relay.get_status() or "Switched from rf to acoustic" in relay.get_status()

def test_send_data_rf(relay):
    relay.switch_link(0.85)  # Switch to RF
    data = b"test_rf"
    success = relay.send_data(data, "rf")
    assert success is True
    assert "Data sent over rf link" in relay.get_status()

def test_send_data_acoustic(relay):
    relay.switch_link(0.65)  # Switch to acoustic
    data = b"test_acoustic"
    success = relay.send_data(data, "acoustic")
    assert success is True
    assert "Data sent over acoustic link" in relay.get_status()

def test_send_data_default_link(relay):
    # Should use current link if not specified
    relay.switch_link(0.85)  # Switch to RF
    data = b"test_default"
    success = relay.send_data(data)
    assert success is True
    assert "Data sent over rf link" in relay.get_status()

def test_status_reporting(relay):
    relay.switch_link(0.85)
    relay.send_data(b"status_test", "rf")
    status = relay.get_status()
    assert isinstance(status, str)
    assert "Data sent over rf link" in status or "Switched from acoustic to rf" in status