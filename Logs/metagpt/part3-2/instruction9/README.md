# MIDI Synth DAW Integrator

## Overview
This program integrates optimized MIDI input handling, synthesizer data analysis from .Wav files, and DAW virtual instrument configuration into a single, user-friendly Python application.

## Features
- **MIDI Input Handling:** List and listen to available MIDI input ports using the `mido` library.
- **Synthesizer Data Analysis:** View synthesizer parameters extracted from .Wav files (see `synth_data.txt`).
- **DAW Configuration Guide:** Access a step-by-step guide for configuring virtual instruments in your DAW (see `daw_virtual_instrument_configuration.md`).

## Included Files
- `midi_synth_daw_integrator.py`: Main integration program.
- `optimized_midi_input.py`: Optimized MIDI input script.
- `synth_data.txt`: Synthesizer data extracted from .Wav analysis.
- `daw_virtual_instrument_configuration.md`: DAW configuration guide.

## Requirements
- Python 3.7+
- `mido` and `python-rtmidi` libraries

Install dependencies:
```bash
pip install mido python-rtmidi
```

## Usage
1. Ensure all required files are in the same directory.
2. Run the main program:
   ```bash
   python midi_synth_daw_integrator.py
   ```
3. Follow the on-screen menu to:
   - List MIDI input ports
   - Listen to MIDI input
   - View synthesizer data
   - Read the DAW configuration guide

## Documentation
- **Synthesizer Data:** See `synth_data.txt` for extracted parameters.
- **DAW Guide:** See `daw_virtual_instrument_configuration.md` for instrument setup instructions.

## Deployment
This program is ready for user deployment. Place all files in your working directory and run the main script as described above.

## Author
Alex
