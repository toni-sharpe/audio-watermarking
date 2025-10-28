# Audio Metadata Extraction

This module provides comprehensive metadata extraction from audio files using librosa and other audio analysis tools.

## Features

The metadata extraction includes:

### Basic Information
- Duration in seconds
- Sample rate (Hz)
- Number of channels (mono/stereo)
- Bit depth
- Total number of samples
- File path

### Musical Characteristics
- Tempo (BPM)
- Estimated musical key with confidence score
- Base/fundamental frequency (Hz)
- Beat count and timing information

### Frequency Band Analysis
Detects and timestamps when different frequency bands are active:
- **Sub-bass**: 20-60 Hz
- **Bass**: 60-250 Hz
- **Mid**: 250-4000 Hz
- **Treble**: 4000-20000 Hz

For each band, the analysis provides:
- Active regions with start/end timestamps
- Mean and max energy levels
- Duration of each active region

### Spectral Features
- Mean spectral centroid (brightness)
- Mean spectral rolloff
- Mean zero crossing rate
- Mean RMS energy

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

Extract metadata from an audio file:

```bash
python audio_metadata.py your_audio_file.wav
```

This will:
1. Analyze the audio file
2. Print the metadata as JSON to stdout
3. Save the metadata to `audio_metadata.json` in the repository root

### Python API

```python
from audio_metadata import extract_audio_metadata

# Extract metadata and save to default location (audio_metadata.json)
metadata = extract_audio_metadata('path/to/audio.wav')

# Or specify a custom output path
metadata = extract_audio_metadata('path/to/audio.wav', 'custom_output.json')

# Access specific metadata
print(f"Duration: {metadata['basic_info']['duration_seconds']} seconds")
print(f"Sample Rate: {metadata['basic_info']['sample_rate_hz']} Hz")
print(f"Estimated Key: {metadata['musical_characteristics']['estimated_key']}")
print(f"Tempo: {metadata['musical_characteristics']['tempo_bpm']} BPM")

# Access frequency band information
for band_name, band_info in metadata['frequency_bands'].items():
    print(f"{band_name}: {len(band_info['active_regions'])} active regions")
    for region in band_info['active_regions'][:3]:  # First 3 regions
        print(f"  {region['start_time_seconds']:.2f}s - {region['end_time_seconds']:.2f}s")
```

## Output Format

The metadata is saved as a JSON file with the following structure:

```json
{
  "basic_info": {
    "duration_seconds": 3.0,
    "sample_rate_hz": 44100,
    "channels": 1,
    "bit_depth": 16,
    "total_samples": 132300,
    "file_path": "audio.wav"
  },
  "musical_characteristics": {
    "tempo_bpm": 120.0,
    "estimated_key": "C",
    "key_confidence": 0.85,
    "base_frequency_hz": 440.0,
    "beat_count": 24,
    "first_beat_time_seconds": 0.5,
    "last_beat_time_seconds": 11.5
  },
  "frequency_bands": {
    "sub_bass_20_60hz": {
      "frequency_range_hz": "20-60",
      "active_regions": [
        {
          "start_time_seconds": 0.0,
          "end_time_seconds": 1.5,
          "duration_seconds": 1.5
        }
      ],
      "mean_energy": 0.15,
      "max_energy": 0.45
    },
    // ... other frequency bands ...
  },
  "spectral_features": {
    "mean_spectral_centroid_hz": 2000.0,
    "mean_spectral_rolloff_hz": 8000.0,
    "mean_zero_crossing_rate": 0.15,
    "mean_rms_energy": 0.3
  }
}
```

## Supported Audio Formats

- WAV files (44.1kHz or 48kHz)
- 16-bit or 24-bit
- Mono or stereo

## Testing

Run the test suite:

```bash
pytest test_metadata.py -v
```

## Examples

### Analyze a music track

```bash
python audio_metadata.py my_song.wav
cat audio_metadata.json | python -m json.tool
```

### Check frequency content

```python
from audio_metadata import extract_audio_metadata
import json

metadata = extract_audio_metadata('bass_heavy_track.wav')

# Check which frequency bands are most active
for band_name, band_info in metadata['frequency_bands'].items():
    print(f"{band_name}: mean energy = {band_info['mean_energy']:.4f}")
```

### Find tempo and key

```python
from audio_metadata import extract_audio_metadata

metadata = extract_audio_metadata('song.wav')
print(f"Tempo: {metadata['musical_characteristics']['tempo_bpm']:.1f} BPM")
print(f"Key: {metadata['musical_characteristics']['estimated_key']}")
```

## Notes

- The frequency band detection uses a threshold-based approach where regions are considered "active" when their energy exceeds the 25th percentile
- Musical key estimation is based on chroma features and may not be accurate for all genres
- Base frequency detection works best with melodic content that has a clear fundamental frequency
- Very short audio files (< 1 second) may produce warnings or less accurate analysis
