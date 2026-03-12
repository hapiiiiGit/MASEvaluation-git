# optimized_midi_input.py
import mido

# List available MIDI input ports
def list_midi_inputs():
    inputs = mido.get_input_names()
    print('Available MIDI input ports:')
    for i, port in enumerate(inputs):
        print(f'{i+1}: {port}')
    return inputs

# Open a MIDI input port and print incoming messages
def listen_to_midi_input(port_name):
    with mido.open_input(port_name) as inport:
        print(f'Listening on {port_name}... Press Ctrl+C to stop.')
        try:
            for msg in inport:
                print(msg)
        except KeyboardInterrupt:
            print('Stopped listening.')

if __name__ == '__main__':
    inputs = list_midi_inputs()
    if inputs:
        # Automatically select the first available port for demo
        listen_to_midi_input(inputs[0])
    else:
        print('No MIDI input ports found.')
