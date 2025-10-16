# Quick Start Guide

## Prerequisites

Before you start, you'll need:
- Python 3.7 or later installed
- Git (to clone the repository)

## Setup

1. **Clone the repository and checkout this PR branch**:
   ```bash
   git clone https://github.com/toni-sharpe/audio-watermarking.git
   cd audio-watermarking
   git checkout copilot/add-audio-upload-feature
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or on Ubuntu/Debian:
   ```bash
   sudo apt-get install python3-flask python3-numpy
   ```

## Running the Application

1. **Make sure you're in the repository directory** (where app.py and index.html are located)

2. **Start the server**:
   ```bash
   python app.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

4. **Upload a WAV file**:
   - Click "Choose File" and select a WAV file (44.1kHz, 16-bit)
   - Click "Upload and Process"
   - The watermarked file will download automatically

## Creating a Test Audio File

If you don't have a test audio file, you can create one using Python:

```python
import wave
import numpy as np

# Generate a 440Hz sine wave (A note) at 44.1kHz, 16-bit
sample_rate = 44100
duration = 1.0
t = np.linspace(0, duration, int(sample_rate * duration))
audio_signal = 0.3 * np.sin(2 * np.pi * 440.0 * t)
audio_signal_int16 = np.int16(audio_signal * 32767)

# Save as WAV
with wave.open('test_audio.wav', 'w') as wav_file:
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_signal_int16.tobytes())
```

## Verifying the Watermark

To verify the watermark was added correctly:

```python
import wave
import numpy as np

# Open the watermarked file
with wave.open('watermarked_test_audio.wav', 'rb') as wav:
    # Read first 10 samples
    frames = wav.readframes(10)
    watermark = np.frombuffer(frames, dtype=np.int16)
    print("Watermark samples:", watermark)
    # Should show: [1, 0, 0, 1, 0, 0, 0, 0, 0, 0]
```

## What the Watermark Does

The application adds 10 samples at the very beginning of your audio file with these amplitudes:
- Sample 1: -90dB → amplitude 1
- Sample 2: -98dB → amplitude 0  
- Sample 3: -95dB → amplitude 0
- Sample 4: -90dB → amplitude 1
- Sample 5: -92dB → amplitude 0
- Sample 6: -92dB → amplitude 0
- Sample 7: -94dB → amplitude 0
- Sample 8: -99dB → amplitude 0
- Sample 9: -92dB → amplitude 0
- Sample 10: -91dB → amplitude 0

These extremely low amplitude values are essentially imperceptible in the audio but serve as a digital watermark.

## Troubleshooting

**Problem**: Server won't start or returns "File not found" error  
**Solution**: Make sure you're in the repository directory where both `app.py` and `index.html` are located. Both files must be in the same directory.

**Problem**: Upload fails with format error  
**Solution**: Ensure your WAV file is exactly 44.1kHz sample rate and 16-bit depth. You can check this with audio editing software or by using the test file creation script above.
