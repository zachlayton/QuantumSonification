import numpy as np
import pyroomacoustics as pra
from scipy.io import wavfile

# 1. Define the simulation parameters
sample_rate = 44100  # CD quality sampling rate (Hz)
absorption_coeff = 0.2  # Surface absorption (0 = fully reflective, 1 = fully absorptive)
max_order = 15  # Maximum number of bounces (reflections) to calculate

# 2. Configure the 3D room geometry (Width, Length, Height) in meters
# This creates a rectangular 3D room: 7m wide x 9m long x 3.5m high
room_dimensions = [7.0, 9.0, 3.5]

# Create the room object using the Image Source Method (ISM)
room = pra.Shoebox(
    room_dimensions,
    fs=sample_rate,
    materials=pra.Material(absorption_coeff),
    max_order=max_order
)

# 3. Add a sound source and a microphone receiver (Coordinates in [X, Y, Z])
source_position = [2.0, 3.5, 1.8]
mic_position = [4.5, 6.0, 1.5]

# The source generates the "impulse" (internally managed by the simulator)
room.add_source(source_position)

# Microphones must be passed as a 2D array where columns are coordinates
mic_array = np.array([mic_position]).T
room.add_microphone_array(pra.MicrophoneArray(mic_array, room.fs))

# 4. Compute the Room Impulse Response (RIR)
room.compute_rir()

# 5. Extract the generated impulse response
# pyroomacoustics stores RIRs in a nested list: room.rir[mic_index][source_index]
rir = room.rir[0][0]

# 6. Normalize and format the audio for .wav export
# Normalize to avoid digital clipping and fit within the floating-point audio range
rir_normalized = rir / np.max(np.abs(rir))

# Ensure data type is float32 (highly standard for DAW and sampler IRs)
rir_wav_data = rir_normalized.astype(np.float32)

# 7. Export to a WAV file
output_filename = "3d_room_impulse_response.wav"
wavfile.write(output_filename, sample_rate, rir_wav_data)

print(f"Success! 3D Room Impulse Response saved as: {output_filename}")
print(f"RIR Length: {len(rir)} samples ({len(rir)/sample_rate:.3f} seconds)")
