#!/usr/bin/env python3
"""
midi_synth_daw_integrator.py

A cohesive Python program that integrates:
- Optimized MIDI input device handling
- Synthesizer data loading from a text file
- Access to DAW virtual instrument configuration guide

All documentation is included and the program is ready for user deployment.

Dependencies:
- mido (for MIDI input handling)
  Install via: pip install mido python-rtmidi

Files required in the same directory:
- optimized_midi_input.py
- synth_data.txt
- daw_virtual_instrument_configuration.md

Author: Alex
Date: 2024-06
"""

import os
import sys
import subprocess

# Paths to required files
MIDI_SCRIPT = "optimized_midi_input.py"
SYNTH_DATA_FILE = "synth_data.txt"
DAW_CONFIG_FILE = "daw_virtual_instrument_configuration.md"

def print_header():
    print("=" * 60)
    print("MIDI Synth DAW Integrator")
    print("=" * 60)
    print("This program integrates MIDI input handling, synthesizer data analysis,")
    print("and DAW configuration documentation for music production workflows.\n")

def check_files():
    missing = []
    for f in [MIDI_SCRIPT, SYNTH_DATA_FILE, DAW_CONFIG_FILE]:
        if not os.path.isfile(f):
            missing.append(f)
    if missing:
        print("ERROR: The following required files are missing:")
        for f in missing:
            print(f"  - {f}")
        print("Please ensure all files are present in the current directory.")
        sys.exit(1)

def show_menu():
    print("Select an option:")
    print("1. List available MIDI input ports")
    print("2. Listen to MIDI input (demo)")
    print("3. Show synthesizer data from .Wav analysis")
    print("4. View DAW virtual instrument configuration guide")
    print("5. Exit")

def run_midi_script_list_inputs():
    # Run the list_midi_inputs() function from optimized_midi_input.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("optimized_midi_input", MIDI_SCRIPT)
    midi_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(midi_module)
    midi_module.list_midi_inputs()

def run_midi_script_listen():
    import importlib.util
    spec = importlib.util.spec_from_file_location("optimized_midi_input", MIDI_SCRIPT)
    midi_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(midi_module)
    inputs = midi_module.list_midi_inputs()
    if not inputs:
        print("No MIDI input ports found.")
        return
    print("\nSelect a MIDI input port to listen to:")
    for i, port in enumerate(inputs):
        print(f"{i+1}: {port}")
    try:
        idx = int(input("Enter port number (default 1): ").strip() or "1")
        if idx < 1 or idx > len(inputs):
            print("Invalid selection.")
            return
        port_name = inputs[idx-1]
        midi_module.listen_to_midi_input(port_name)
    except ValueError:
        print("Invalid input.")

def show_synth_data():
    print("\nSynthesizer Data Extracted from .Wav File:")
    print("-" * 45)
    try:
        with open(SYNTH_DATA_FILE, "r") as f:
            for line in f:
                print(line.strip())
    except Exception as e:
        print(f"Error reading {SYNTH_DATA_FILE}: {e}")

def view_daw_config_guide():
    print("\nDAW Virtual Instrument Configuration Guide:")
    print("-" * 45)
    try:
        with open(DAW_CONFIG_FILE, "r") as f:
            for line in f:
                print(line.rstrip())
    except Exception as e:
        print(f"Error reading {DAW_CONFIG_FILE}: {e}")

def main():
    print_header()
    check_files()
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice == "1":
            run_midi_script_list_inputs()
        elif choice == "2":
            run_midi_script_listen()
        elif choice == "3":
            show_synth_data()
        elif choice == "4":
            view_daw_config_guide()
        elif choice == "5":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.\n")

if __name__ == "__main__":
    main()