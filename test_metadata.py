import pytest
import numpy as np
import wave
import tempfile
import os
import json
from audio_metadata import (
    extract_audio_metadata,
    save_metadata_to_json,
    extract_and_save_metadata
)


def create_test_audio_file(filename, duration_seconds=2, sample_rate=44100, n_channels=1):
    """Helper function to create a test audio file with some frequency content"""
    duration_samples = int(duration_seconds * sample_rate)
    
    # Generate audio with multiple frequencies
    t = np.linspace(0, duration_seconds, duration_samples)
    # Add frequencies: 50Hz (sub-bass), 150Hz (bass), 800Hz (mid), 5000Hz (treble)
    audio = (np.sin(2 * np.pi * 50 * t) * 0.2 + 
             np.sin(2 * np.pi * 150 * t) * 0.2 + 
             np.sin(2 * np.pi * 800 * t) * 0.3 + 
             np.sin(2 * np.pi * 5000 * t) * 0.3)
    
    # Convert to int16
    audio = (audio * 32767).astype(np.int16)
    
    # Make stereo if needed
    if n_channels == 2:
        audio = np.column_stack([audio, audio])
    
    # Save to WAV file
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())


class TestAudioMetadata:
    """Test suite for audio metadata extraction"""
    
    def test_extract_basic_metadata(self):
        """Test extraction of basic audio metadata"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            test_file = f.name
        
        try:
            # Create test audio file
            create_test_audio_file(test_file, duration_seconds=2, sample_rate=44100, n_channels=2)
            
            # Extract metadata
            metadata = extract_audio_metadata(test_file)
            
            # Verify basic info is present
            assert 'basic_info' in metadata
            assert metadata['basic_info']['channels'] == 2
            assert metadata['basic_info']['sample_rate'] == 44100
            assert metadata['basic_info']['bit_depth'] == 16
            assert abs(metadata['basic_info']['duration_seconds'] - 2.0) < 0.1
            
            # Verify duration
            assert 'duration_seconds' in metadata
            assert abs(metadata['duration_seconds'] - 2.0) < 0.1
            
            # Verify timestamp is present
            assert 'extraction_timestamp' in metadata
            
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_extract_frequency_ranges(self):
        """Test extraction of frequency range information"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            test_file = f.name
        
        try:
            # Create test audio file with known frequencies
            create_test_audio_file(test_file, duration_seconds=2)
            
            # Extract metadata
            metadata = extract_audio_metadata(test_file)
            
            # Verify frequency ranges are present
            assert 'frequency_ranges' in metadata
            
            freq_ranges = metadata['frequency_ranges']
            assert 'sub_bass' in freq_ranges
            assert 'bass' in freq_ranges
            assert 'mid' in freq_ranges
            assert 'treble' in freq_ranges
            
            # Each range should have frequency_range_hz, mean_energy, max_energy
            for range_name in ['sub_bass', 'bass', 'mid', 'treble']:
                assert 'frequency_range_hz' in freq_ranges[range_name]
                assert 'mean_energy' in freq_ranges[range_name]
                assert 'max_energy' in freq_ranges[range_name]
                assert 'prominent_regions' in freq_ranges[range_name]
            
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_extract_spectral_features(self):
        """Test extraction of spectral features"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            test_file = f.name
        
        try:
            # Create test audio file
            create_test_audio_file(test_file, duration_seconds=2)
            
            # Extract metadata
            metadata = extract_audio_metadata(test_file)
            
            # Verify spectral features are present
            assert 'spectral_features' in metadata
            
            spectral = metadata['spectral_features']
            assert 'mean_spectral_centroid_hz' in spectral
            assert 'mean_spectral_rolloff_hz' in spectral
            assert 'mean_spectral_bandwidth_hz' in spectral
            
            # Values should be positive
            assert spectral['mean_spectral_centroid_hz'] > 0
            assert spectral['mean_spectral_rolloff_hz'] > 0
            assert spectral['mean_spectral_bandwidth_hz'] > 0
            
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_extract_musical_key(self):
        """Test extraction of musical key"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            test_file = f.name
        
        try:
            # Create test audio file
            create_test_audio_file(test_file, duration_seconds=2)
            
            # Extract metadata
            metadata = extract_audio_metadata(test_file)
            
            # Verify musical key is present
            assert 'musical_key' in metadata
            
            key_info = metadata['musical_key']
            assert 'estimated_key' in key_info
            assert 'key_index' in key_info
            assert 'confidence' in key_info
            
            # Key should be one of the 12 notes
            valid_keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            assert key_info['estimated_key'] in valid_keys
            
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_save_metadata_to_json(self):
        """Test saving metadata to JSON file"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:
            
            audio_path = audio_file.name
            json_path = json_file.name
        
        try:
            # Create test audio file
            create_test_audio_file(audio_path, duration_seconds=1)
            
            # Extract metadata
            metadata = extract_audio_metadata(audio_path)
            
            # Save to JSON
            save_metadata_to_json(metadata, json_path)
            
            # Verify JSON file was created
            assert os.path.exists(json_path)
            
            # Load and verify JSON content
            with open(json_path, 'r') as f:
                loaded_metadata = json.load(f)
            
            assert loaded_metadata == metadata
            assert 'basic_info' in loaded_metadata
            assert 'duration_seconds' in loaded_metadata
            
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(json_path):
                os.remove(json_path)
    
    def test_extract_and_save_metadata(self):
        """Test combined extraction and saving to JSON"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:
            
            audio_path = audio_file.name
            json_path = json_file.name
        
        try:
            # Create test audio file
            create_test_audio_file(audio_path, duration_seconds=1)
            
            # Extract and save metadata
            metadata = extract_and_save_metadata(audio_path, json_path)
            
            # Verify JSON file was created
            assert os.path.exists(json_path)
            
            # Load and verify JSON content
            with open(json_path, 'r') as f:
                loaded_metadata = json.load(f)
            
            # Verify metadata was returned
            assert metadata is not None
            assert 'basic_info' in metadata
            
            # Verify saved metadata matches returned metadata
            assert loaded_metadata == metadata
            
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(json_path):
                os.remove(json_path)
    
    def test_extract_rhythm_features(self):
        """Test extraction of rhythm and tempo features"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            test_file = f.name
        
        try:
            # Create test audio file
            create_test_audio_file(test_file, duration_seconds=3)
            
            # Extract metadata
            metadata = extract_audio_metadata(test_file)
            
            # Verify rhythm info is present
            assert 'rhythm' in metadata
            
            rhythm = metadata['rhythm']
            assert 'tempo_bpm' in rhythm
            assert 'beat_count' in rhythm
            assert 'beat_timestamps' in rhythm
            
            # Tempo should be a number (even if 0 for non-rhythmic content)
            assert isinstance(rhythm['tempo_bpm'], (int, float))
            
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_mono_vs_stereo(self):
        """Test metadata extraction for both mono and stereo files"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as mono_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as stereo_file:
            
            mono_path = mono_file.name
            stereo_path = stereo_file.name
        
        try:
            # Create mono and stereo files
            create_test_audio_file(mono_path, duration_seconds=1, n_channels=1)
            create_test_audio_file(stereo_path, duration_seconds=1, n_channels=2)
            
            # Extract metadata for both
            mono_metadata = extract_audio_metadata(mono_path)
            stereo_metadata = extract_audio_metadata(stereo_path)
            
            # Verify channel counts
            assert mono_metadata['basic_info']['channels'] == 1
            assert stereo_metadata['basic_info']['channels'] == 2
            
            # Both should have similar spectral features (since content is similar)
            assert 'spectral_features' in mono_metadata
            assert 'spectral_features' in stereo_metadata
            
        finally:
            if os.path.exists(mono_path):
                os.remove(mono_path)
            if os.path.exists(stereo_path):
                os.remove(stereo_path)
