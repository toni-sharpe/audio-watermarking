"""
Audio Metadata Extraction Module

This module provides functionality to extract comprehensive metadata from audio files,
including basic properties, frequency band analysis, and musical characteristics.
"""

import wave
import numpy as np
import librosa
import json
from pathlib import Path


def extract_audio_metadata(audio_file_path, output_json_path=None):
    """
    Extract comprehensive metadata from an audio file.
    
    Args:
        audio_file_path: Path to the audio file (WAV format)
        output_json_path: Optional path for the JSON output. If None, uses 'audio_metadata.json' in repo root
        
    Returns:
        dict: Dictionary containing all extracted metadata
    """
    # Load audio file
    y, sr = librosa.load(audio_file_path, sr=None, mono=False)
    
    # Get WAV file properties
    with wave.open(audio_file_path, 'rb') as wav_file:
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
    
    # Convert to mono for analysis if stereo
    y_mono = librosa.to_mono(y) if len(y.shape) > 1 else y
    
    # Basic metadata
    duration = librosa.get_duration(y=y_mono, sr=sr)
    
    # Frequency band analysis
    frequency_bands = analyze_frequency_bands(y_mono, sr)
    
    # Musical characteristics
    tempo, beat_frames = librosa.beat.beat_track(y=y_mono, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Estimate musical key
    chroma = librosa.feature.chroma_cqt(y=y_mono, sr=sr)
    key_info = estimate_key(chroma)
    
    # Base/fundamental frequency estimation
    base_frequency = estimate_base_frequency(y_mono, sr)
    
    # Spectral features
    spectral_centroids = librosa.feature.spectral_centroid(y=y_mono, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y_mono, sr=sr)[0]
    
    # Zero crossing rate
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y_mono)[0]
    
    # RMS energy
    rms = librosa.feature.rms(y=y_mono)[0]
    
    # Compile metadata
    metadata = {
        "basic_info": {
            "duration_seconds": float(duration),
            "sample_rate_hz": int(sr),
            "channels": int(n_channels),
            "bit_depth": int(sample_width * 8),
            "total_samples": int(n_frames),
            "file_path": str(audio_file_path)
        },
        "musical_characteristics": {
            "tempo_bpm": float(tempo),
            "estimated_key": key_info["key"],
            "key_confidence": float(key_info["confidence"]),
            "base_frequency_hz": float(base_frequency) if base_frequency else None,
            "beat_count": int(len(beat_times)),
            "first_beat_time_seconds": float(beat_times[0]) if len(beat_times) > 0 else None,
            "last_beat_time_seconds": float(beat_times[-1]) if len(beat_times) > 0 else None
        },
        "frequency_bands": frequency_bands,
        "spectral_features": {
            "mean_spectral_centroid_hz": float(np.mean(spectral_centroids)),
            "mean_spectral_rolloff_hz": float(np.mean(spectral_rolloff)),
            "mean_zero_crossing_rate": float(np.mean(zero_crossing_rate)),
            "mean_rms_energy": float(np.mean(rms))
        }
    }
    
    # Save to JSON file
    if output_json_path is None:
        # Get the repository root (parent of the audio file if not specified)
        output_json_path = Path(__file__).parent / "audio_metadata.json"
    
    with open(output_json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return metadata


def analyze_frequency_bands(y, sr):
    """
    Analyze audio and identify timestamps where different frequency bands are active.
    
    Frequency band definitions:
    - Sub-bass: 20-60 Hz
    - Bass: 60-250 Hz
    - Mid: 250-4000 Hz
    - Treble: 4000-20000 Hz
    
    Args:
        y: Audio time series
        sr: Sample rate
        
    Returns:
        dict: Dictionary with frequency band information and timestamps
    """
    # Compute Short-Time Fourier Transform
    D = librosa.stft(y)
    S, phase = librosa.magphase(D)
    
    # Get frequencies for each bin
    frequencies = librosa.fft_frequencies(sr=sr)
    
    # Define frequency band indices
    sub_bass_idx = np.where((frequencies >= 20) & (frequencies < 60))[0]
    bass_idx = np.where((frequencies >= 60) & (frequencies < 250))[0]
    mid_idx = np.where((frequencies >= 250) & (frequencies < 4000))[0]
    treble_idx = np.where((frequencies >= 4000) & (frequencies <= 20000))[0]
    
    # Calculate energy in each band over time
    times = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr)
    
    sub_bass_energy = np.mean(S[sub_bass_idx, :], axis=0)
    bass_energy = np.mean(S[bass_idx, :], axis=0)
    mid_energy = np.mean(S[mid_idx, :], axis=0)
    treble_energy = np.mean(S[treble_idx, :], axis=0)
    
    # Find active regions (where energy is above threshold)
    threshold_percentile = 25  # Energy must be above 25th percentile to be considered active
    
    def find_active_regions(energy, times, threshold_percentile=25):
        """Find start and end times of active regions"""
        threshold = np.percentile(energy, threshold_percentile)
        active = energy > threshold
        
        # Find transitions
        transitions = np.diff(active.astype(int))
        starts = np.where(transitions == 1)[0] + 1
        ends = np.where(transitions == -1)[0] + 1
        
        # Handle edge cases
        if active[0]:
            starts = np.concatenate([[0], starts])
        if active[-1]:
            ends = np.concatenate([ends, [len(active) - 1]])
        
        regions = []
        for start, end in zip(starts, ends):
            regions.append({
                "start_time_seconds": float(times[start]),
                "end_time_seconds": float(times[end]),
                "duration_seconds": float(times[end] - times[start])
            })
        
        return regions
    
    frequency_bands = {
        "sub_bass_20_60hz": {
            "frequency_range_hz": "20-60",
            "active_regions": find_active_regions(sub_bass_energy, times, threshold_percentile),
            "mean_energy": float(np.mean(sub_bass_energy)),
            "max_energy": float(np.max(sub_bass_energy))
        },
        "bass_60_250hz": {
            "frequency_range_hz": "60-250",
            "active_regions": find_active_regions(bass_energy, times, threshold_percentile),
            "mean_energy": float(np.mean(bass_energy)),
            "max_energy": float(np.max(bass_energy))
        },
        "mid_250_4000hz": {
            "frequency_range_hz": "250-4000",
            "active_regions": find_active_regions(mid_energy, times, threshold_percentile),
            "mean_energy": float(np.mean(mid_energy)),
            "max_energy": float(np.max(mid_energy))
        },
        "treble_4000_20000hz": {
            "frequency_range_hz": "4000-20000",
            "active_regions": find_active_regions(treble_energy, times, threshold_percentile),
            "mean_energy": float(np.mean(treble_energy)),
            "max_energy": float(np.max(treble_energy))
        }
    }
    
    return frequency_bands


def estimate_key(chroma):
    """
    Estimate the musical key from chroma features.
    
    Args:
        chroma: Chroma feature matrix
        
    Returns:
        dict: Dictionary with estimated key and confidence
    """
    # Average chroma across time
    chroma_mean = np.mean(chroma, axis=1)
    
    # Pitch class names
    pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Find the pitch class with maximum energy
    key_idx = np.argmax(chroma_mean)
    key = pitch_classes[key_idx]
    
    # Calculate confidence as the ratio of max to sum
    confidence = chroma_mean[key_idx] / np.sum(chroma_mean)
    
    return {
        "key": key,
        "confidence": confidence
    }


def estimate_base_frequency(y, sr):
    """
    Estimate the base/fundamental frequency of the audio.
    
    Args:
        y: Audio time series
        sr: Sample rate
        
    Returns:
        float: Estimated fundamental frequency in Hz, or None if cannot be estimated
    """
    # Use piptrack to estimate pitch
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    # Get the pitch with highest magnitude at each time frame
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        if pitch > 0:  # Only consider non-zero pitches
            pitch_values.append(pitch)
    
    if pitch_values:
        # Return the median pitch as the base frequency
        return np.median(pitch_values)
    else:
        return None


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        metadata = extract_audio_metadata(audio_file)
        print(json.dumps(metadata, indent=2))
    else:
        print("Usage: python audio_metadata.py <audio_file.wav>")
