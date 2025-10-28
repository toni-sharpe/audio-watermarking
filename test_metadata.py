"""
Tests for audio metadata extraction functionality
"""

import pytest
import numpy as np
import wave
import tempfile
import os
import json
from audio_metadata import (
    extract_audio_metadata,
    analyze_frequency_bands,
    estimate_key,
    estimate_base_frequency
)


def create_test_audio_with_tone(filename, frequency=440, duration_seconds=2, sample_rate=44100, n_channels=1):
    """
    Create a test WAV file with a specific tone frequency.
    
    Args:
        filename: Output filename
        frequency: Frequency of the tone in Hz
        duration_seconds: Duration in seconds
        sample_rate: Sample rate in Hz
        n_channels: Number of channels (1=mono, 2=stereo)
    """
    # Generate sine wave
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
    audio_data = (np.sin(2 * np.pi * frequency * t) * 32767 * 0.5).astype(np.int16)
    
    if n_channels == 2:
        audio_data = np.column_stack([audio_data, audio_data])
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())


class TestAudioMetadataExtraction:
    """Test suite for audio metadata extraction"""
    
    def test_extract_basic_metadata_mono(self):
        """Test extraction of basic metadata from mono audio"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:
            
            audio_path = audio_file.name
            json_path = json_file.name
            
            try:
                # Create test audio (A440 tone, 2 seconds)
                create_test_audio_with_tone(audio_path, frequency=440, duration_seconds=2, n_channels=1)
                
                # Extract metadata
                metadata = extract_audio_metadata(audio_path, json_path)
                
                # Verify basic info
                assert "basic_info" in metadata
                assert metadata["basic_info"]["channels"] == 1
                assert metadata["basic_info"]["sample_rate_hz"] == 44100
                assert metadata["basic_info"]["bit_depth"] == 16
                assert 1.9 < metadata["basic_info"]["duration_seconds"] < 2.1  # Allow some tolerance
                
                # Verify musical characteristics
                assert "musical_characteristics" in metadata
                assert "tempo_bpm" in metadata["musical_characteristics"]
                assert "estimated_key" in metadata["musical_characteristics"]
                
                # Verify frequency bands
                assert "frequency_bands" in metadata
                assert "sub_bass_20_60hz" in metadata["frequency_bands"]
                assert "bass_60_250hz" in metadata["frequency_bands"]
                assert "mid_250_4000hz" in metadata["frequency_bands"]
                assert "treble_4000_20000hz" in metadata["frequency_bands"]
                
                # Verify spectral features
                assert "spectral_features" in metadata
                assert "mean_spectral_centroid_hz" in metadata["spectral_features"]
                
                # Verify JSON file was created
                assert os.path.exists(json_path)
                with open(json_path, 'r') as f:
                    saved_metadata = json.load(f)
                assert saved_metadata == metadata
                
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(json_path):
                    os.remove(json_path)
    
    def test_extract_basic_metadata_stereo(self):
        """Test extraction of basic metadata from stereo audio"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:
            
            audio_path = audio_file.name
            json_path = json_file.name
            
            try:
                # Create test audio (A440 tone, 2 seconds, stereo)
                create_test_audio_with_tone(audio_path, frequency=440, duration_seconds=2, n_channels=2)
                
                # Extract metadata
                metadata = extract_audio_metadata(audio_path, json_path)
                
                # Verify stereo channel count
                assert metadata["basic_info"]["channels"] == 2
                
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(json_path):
                    os.remove(json_path)
    
    def test_frequency_bands_detection(self):
        """Test that frequency bands are correctly identified"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:
            
            audio_path = audio_file.name
            json_path = json_file.name
            
            try:
                # Create test audio with a mid-range frequency
                create_test_audio_with_tone(audio_path, frequency=1000, duration_seconds=1)
                
                # Extract metadata
                metadata = extract_audio_metadata(audio_path, json_path)
                
                # The 1000Hz tone should have most energy in the mid range (250-4000Hz)
                mid_energy = metadata["frequency_bands"]["mid_250_4000hz"]["mean_energy"]
                bass_energy = metadata["frequency_bands"]["bass_60_250hz"]["mean_energy"]
                
                # Mid should have significantly more energy than bass for a 1000Hz tone
                assert mid_energy > bass_energy
                
                # Check that active regions are detected
                assert "active_regions" in metadata["frequency_bands"]["mid_250_4000hz"]
                assert len(metadata["frequency_bands"]["mid_250_4000hz"]["active_regions"]) > 0
                
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(json_path):
                    os.remove(json_path)
    
    def test_base_frequency_estimation(self):
        """Test base frequency estimation"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:
            
            audio_path = audio_file.name
            json_path = json_file.name
            
            try:
                # Create test audio with A440 (standard tuning)
                create_test_audio_with_tone(audio_path, frequency=440, duration_seconds=1)
                
                # Extract metadata
                metadata = extract_audio_metadata(audio_path, json_path)
                
                # Base frequency should be close to 440Hz
                base_freq = metadata["musical_characteristics"]["base_frequency_hz"]
                
                if base_freq is not None:  # May be None if detection fails
                    # Allow for some tolerance in frequency detection
                    assert 400 < base_freq < 480, f"Expected base frequency near 440Hz, got {base_freq}Hz"
                
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(json_path):
                    os.remove(json_path)
    
    def test_json_output_structure(self):
        """Test that JSON output has the correct structure"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file:
            
            audio_path = audio_file.name
            json_path = json_file.name
            
            try:
                # Create test audio
                create_test_audio_with_tone(audio_path, frequency=440, duration_seconds=1)
                
                # Extract metadata
                metadata = extract_audio_metadata(audio_path, json_path)
                
                # Verify all required top-level keys exist
                required_keys = ["basic_info", "musical_characteristics", "frequency_bands", "spectral_features"]
                for key in required_keys:
                    assert key in metadata, f"Missing required key: {key}"
                
                # Verify basic_info structure
                basic_info_keys = ["duration_seconds", "sample_rate_hz", "channels", "bit_depth", "total_samples", "file_path"]
                for key in basic_info_keys:
                    assert key in metadata["basic_info"], f"Missing basic_info key: {key}"
                
                # Verify frequency_bands structure
                band_keys = ["sub_bass_20_60hz", "bass_60_250hz", "mid_250_4000hz", "treble_4000_20000hz"]
                for band in band_keys:
                    assert band in metadata["frequency_bands"], f"Missing frequency band: {band}"
                    assert "active_regions" in metadata["frequency_bands"][band]
                    assert "mean_energy" in metadata["frequency_bands"][band]
                
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(json_path):
                    os.remove(json_path)
    
    def test_default_json_path(self):
        """Test that default JSON path works correctly"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
            audio_path = audio_file.name
            
            try:
                # Create test audio
                create_test_audio_with_tone(audio_path, frequency=440, duration_seconds=1)
                
                # Extract metadata with default path
                metadata = extract_audio_metadata(audio_path)
                
                # Check that default file was created in the repository root
                default_json_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 
                    "audio_metadata.json"
                )
                assert os.path.exists(default_json_path), "Default JSON file should be created"
                
                # Clean up the default file
                if os.path.exists(default_json_path):
                    os.remove(default_json_path)
                
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
