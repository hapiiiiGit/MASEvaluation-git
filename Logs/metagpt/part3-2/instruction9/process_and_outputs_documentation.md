# Documentation: MIDI Input Optimization & Synthesizer Data Generation

## 1. Optimized Python Script for MIDI Input Devices
- **File:** `optimized_midi_input.py`
- **Description:**
    - Lists available MIDI input ports using the `mido` library.
    - Opens the first available port and prints incoming MIDI messages.
- **Usage:**
    - Run the script. It will display available MIDI ports and listen for messages.

## 2. Synthesizer Data Generation from .Wav File
- **File:** `sample_sine.wav` (generated programmatically)
- **Analysis Script:**
    - Generates a sine wave .Wav file.
    - Analyzes the file to extract peak frequency and amplitude envelope.
    - Writes results to `synth_data.txt`.
- **Synthesizer Data Output Example (`synth_data.txt`):**
    ```
    peak_frequency: 440.0
    max_amplitude: 0.5
    min_amplitude: 0.5
    duration: 2.0
    sample_rate: 44100
    ```

## 3. How to Reproduce
- Ensure Python and required libraries (`numpy`, `mido`, `scipy`) are installed.
- Run `optimized_midi_input.py` for MIDI input handling.
- Run the provided analysis code to generate and analyze a .Wav file.
- Review `synth_data.txt` for synthesizer parameters.

## 4. Notes
- The process is fully automated for demonstration purposes.
- You can replace `sample_sine.wav` with any .Wav file for analysis.
