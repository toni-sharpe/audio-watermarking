# Quick Start Guide

## Running the Application

1. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```
   
   Or on Ubuntu/Debian:
   ```bash
   sudo apt-get install python3-flask python3-numpy
   ```

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

### Why Different dB Values Become 0s and 1s

The dB values specified (-90 to -99 dB) are **extremely low amplitudes** - representing sound levels close to silence. Here's how they convert to 16-bit integer values:

**The conversion formula is:**
```
amplitude = 10^(dB/20) × 32767
```

Where 32767 is the maximum value for a signed 16-bit integer.

**For each dB value:**
- **-90dB** → 10^(-90/20) × 32767 = 10^(-4.5) × 32767 ≈ **1.03** → `int()` truncates to **1**
- **-91dB** → 10^(-91/20) × 32767 = 10^(-4.55) × 32767 ≈ **0.92** → `int()` truncates to **0**
- **-92dB** → 10^(-92/20) × 32767 = 10^(-4.6) × 32767 ≈ **0.82** → `int()` truncates to **0**
- **-94dB** → 10^(-94/20) × 32767 = 10^(-4.7) × 32767 ≈ **0.65** → `int()` truncates to **0**
- **-95dB** → 10^(-95/20) × 32767 = 10^(-4.75) × 32767 ≈ **0.58** → `int()` truncates to **0**
- **-98dB** → 10^(-98/20) × 32767 = 10^(-4.9) × 32767 ≈ **0.41** → `int()` truncates to **0**
- **-99dB** → 10^(-99/20) × 32767 = 10^(-4.95) × 32767 ≈ **0.37** → `int()` truncates to **0**

**The key insight:** When you convert these very low dB values and use Python's `int()` function (which truncates toward zero), you get values that are either 0 or 1. These extremely small amplitude values are imperceptible in the audio but serve as a digital watermark.

**Final watermark pattern:**
- Sample 1: -90dB → amplitude **1** (exact: 1.0362)
- Sample 2: -98dB → amplitude **0** (exact: 0.4125)
- Sample 3: -95dB → amplitude **0** (exact: 0.5827)
- Sample 4: -90dB → amplitude **1** (exact: 1.0362)
- Sample 5: -92dB → amplitude **0** (exact: 0.8231)
- Sample 6: -92dB → amplitude **0** (exact: 0.8231)
- Sample 7: -94dB → amplitude **0** (exact: 0.6538)
- Sample 8: -99dB → amplitude **0** (exact: 0.3677)
- Sample 9: -92dB → amplitude **0** (exact: 0.8231)
- Sample 10: -91dB → amplitude **0** (exact: 0.9235)

These extremely low amplitude values are essentially imperceptible in the audio but serve as a digital watermark identifier.
