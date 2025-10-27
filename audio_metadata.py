"""
Audio metadata extraction module using librosa and wave
"""
import numpy as np
import wave
import librosa
import json
from datetime import datetime


# Frequency ranges (in Hz)
FREQ_RANGES = {
    'sub_bass': (20, 60),
    'bass': (60, 250),
    'mid': (250, 2000),
    'treble': (2000, 20000)
}


def extract_audio_metadata(audio_file_path):
    """
    Extract comprehensive metadata from an audio file
    
    Args:
        audio_file_path: Path to the audio file (WAV format)
    
    Returns:
        dict: Dictionary containing extracted metadata
    """
    metadata = {
        'extraction_timestamp': datetime.now().isoformat(),
        'file_path': audio_file_path
    }
    
    # Extract basic WAV file information using wave module
    try:
        with wave.open(audio_file_path, 'rb') as wav_file:
            metadata['basic_info'] = {
                'channels': wav_file.getnchannels(),
                'sample_width_bytes': wav_file.getsampwidth(),
                'bit_depth': wav_file.getsampwidth() * 8,
                'sample_rate': wav_file.getframerate(),
                'total_frames': wav_file.getnframes(),
                'duration_seconds': wav_file.getnframes() / wav_file.getframerate()
            }
    except Exception as e:
        metadata['basic_info_error'] = str(e)
    
    # Load audio with librosa for advanced analysis
    try:
        # Load audio (mono for analysis)
        y, sr = librosa.load(audio_file_path, sr=None, mono=True)
        
        # Duration
        duration = librosa.get_duration(y=y, sr=sr)
        metadata['duration_seconds'] = duration
        
        # Tempo and beat information
        try:
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)
            metadata['rhythm'] = {
                'tempo_bpm': float(tempo),
                'beat_count': len(beats),
                'beat_timestamps': beat_times.tolist() if len(beat_times) > 0 else []
            }
        except Exception as e:
            metadata['rhythm_error'] = str(e)
        
        # Key detection using chroma features
        try:
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            # Get the most prominent chroma (key)
            chroma_vals = np.mean(chroma, axis=1)
            key_index = np.argmax(chroma_vals)
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            metadata['musical_key'] = {
                'estimated_key': keys[key_index],
                'key_index': int(key_index),
                'confidence': float(chroma_vals[key_index])
            }
        except Exception as e:
            metadata['musical_key_error'] = str(e)
        
        # Fundamental frequency (pitch) estimation
        try:
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            # Get the pitch with highest magnitude at each time
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:  # Only include non-zero pitches
                    pitch_values.append(pitch)
            
            if pitch_values:
                metadata['fundamental_frequency'] = {
                    'mean_hz': float(np.mean(pitch_values)),
                    'median_hz': float(np.median(pitch_values)),
                    'min_hz': float(np.min(pitch_values)),
                    'max_hz': float(np.max(pitch_values))
                }
            else:
                metadata['fundamental_frequency'] = None
        except Exception as e:
            metadata['fundamental_frequency_error'] = str(e)
        
        # Spectral features
        try:
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            
            metadata['spectral_features'] = {
                'mean_spectral_centroid_hz': float(np.mean(spectral_centroids)),
                'mean_spectral_rolloff_hz': float(np.mean(spectral_rolloff)),
                'mean_spectral_bandwidth_hz': float(np.mean(spectral_bandwidth))
            }
        except Exception as e:
            metadata['spectral_features_error'] = str(e)
        
        # Frequency range analysis (bass, mid, treble, sub-bass)
        try:
            # Compute STFT
            D = librosa.stft(y)
            magnitude = np.abs(D)
            frequencies = librosa.fft_frequencies(sr=sr)
            
            # Analyze each frequency range over time
            frequency_ranges = {}
            for range_name, (freq_min, freq_max) in FREQ_RANGES.items():
                # Find frequency bins in this range
                freq_mask = (frequencies >= freq_min) & (frequencies < freq_max)
                
                # Get magnitude in this frequency range over time
                range_magnitude = magnitude[freq_mask, :]
                
                # Calculate energy in this range over time
                range_energy = np.sum(range_magnitude, axis=0)
                
                # Find timestamps where this range is prominent
                # Use threshold of 50% of max energy
                threshold = 0.5 * np.max(range_energy) if np.max(range_energy) > 0 else 0
                prominent_frames = np.where(range_energy > threshold)[0]
                
                if len(prominent_frames) > 0:
                    # Find contiguous regions (start/end timestamps)
                    regions = []
                    start_frame = prominent_frames[0]
                    
                    for i in range(1, len(prominent_frames)):
                        # If gap between frames is more than 10 frames, it's a new region
                        if prominent_frames[i] - prominent_frames[i-1] > 10:
                            end_frame = prominent_frames[i-1]
                            start_time = librosa.frames_to_time(start_frame, sr=sr)
                            end_time = librosa.frames_to_time(end_frame, sr=sr)
                            regions.append({
                                'start_seconds': float(start_time),
                                'end_seconds': float(end_time)
                            })
                            start_frame = prominent_frames[i]
                    
                    # Add the last region
                    end_frame = prominent_frames[-1]
                    start_time = librosa.frames_to_time(start_frame, sr=sr)
                    end_time = librosa.frames_to_time(end_frame, sr=sr)
                    regions.append({
                        'start_seconds': float(start_time),
                        'end_seconds': float(end_time)
                    })
                    
                    frequency_ranges[range_name] = {
                        'frequency_range_hz': [freq_min, freq_max],
                        'mean_energy': float(np.mean(range_energy)),
                        'max_energy': float(np.max(range_energy)),
                        'prominent_regions': regions
                    }
                else:
                    frequency_ranges[range_name] = {
                        'frequency_range_hz': [freq_min, freq_max],
                        'mean_energy': 0,
                        'max_energy': 0,
                        'prominent_regions': []
                    }
            
            metadata['frequency_ranges'] = frequency_ranges
        except Exception as e:
            metadata['frequency_ranges_error'] = str(e)
        
        # Zero crossing rate
        try:
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            metadata['zero_crossing_rate'] = {
                'mean': float(np.mean(zcr)),
                'std': float(np.std(zcr))
            }
        except Exception as e:
            metadata['zero_crossing_rate_error'] = str(e)
        
        # RMS energy
        try:
            rms = librosa.feature.rms(y=y)[0]
            metadata['rms_energy'] = {
                'mean': float(np.mean(rms)),
                'max': float(np.max(rms)),
                'min': float(np.min(rms))
            }
        except Exception as e:
            metadata['rms_energy_error'] = str(e)
            
    except Exception as e:
        metadata['librosa_analysis_error'] = str(e)
    
    return metadata


def save_metadata_to_json(metadata, output_path):
    """
    Save metadata dictionary to a JSON file
    
    Args:
        metadata: Dictionary containing metadata
        output_path: Path where JSON file should be saved
    """
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def extract_and_save_metadata(audio_file_path, json_output_path):
    """
    Extract metadata from audio file and save to JSON
    
    Args:
        audio_file_path: Path to the audio file
        json_output_path: Path where JSON file should be saved
    
    Returns:
        dict: The extracted metadata
    """
    metadata = extract_audio_metadata(audio_file_path)
    save_metadata_to_json(metadata, json_output_path)
    return metadata
