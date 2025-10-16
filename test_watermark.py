import pytest
import numpy as np
import wave
import tempfile
import os
import app
from app import add_watermark_samples, remove_watermark_samples, DB_VALUES


def create_test_wav(filename, duration_samples=1000, n_channels=1, sample_rate=44100, sample_width=2):
    """Helper function to create a test WAV file"""
    # Generate silent audio data
    audio_data = np.zeros(duration_samples, dtype=np.int16)
    
    if n_channels == 2:
        audio_data = np.column_stack([audio_data, audio_data])
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.astype(np.int16).tobytes())


def read_wav_samples(filename, n_channels=1):
    """Helper function to read samples from a WAV file"""
    with wave.open(filename, 'rb') as wav_file:
        n_frames = wav_file.getnframes()
        frames = wav_file.readframes(n_frames)
        audio_data = np.frombuffer(frames, dtype=np.int16)
        
        if n_channels == 2:
            audio_data = audio_data.reshape(-1, 2)
    
    return audio_data


class TestWatermarkFunctions:
    """Test suite for watermark functions"""
    
    def test_add_watermark_samples_mono(self):
        """Test adding watermark samples to a mono audio file"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            
            input_path = input_file.name
            output_path = output_file.name
            
            try:
                # Create test audio file
                create_test_wav(input_path, duration_samples=1000, n_channels=1)
                
                # Add watermark
                add_watermark_samples(input_path, output_path)
                
                # Read output and verify
                output_data = read_wav_samples(output_path, n_channels=1)
                
                # Should have 16 more samples than input (1000 + 16 = 1016)
                assert len(output_data) == 1016, f"Expected 1016 samples, got {len(output_data)}"
                
                # Verify first 16 samples are watermark
                # They should be non-zero and follow the pattern
                assert np.any(output_data[:16] != 0), "Watermark samples should not be all zeros"
                
            finally:
                # Clean up
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
    
    def test_add_watermark_samples_stereo(self):
        """Test adding watermark samples to a stereo audio file"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            
            input_path = input_file.name
            output_path = output_file.name
            
            try:
                # Create test audio file
                create_test_wav(input_path, duration_samples=1000, n_channels=2)
                
                # Add watermark
                add_watermark_samples(input_path, output_path)
                
                # Read output and verify
                output_data = read_wav_samples(output_path, n_channels=2)
                
                # Should have 16 more samples than input (1000 + 16 = 1016)
                assert len(output_data) == 1016, f"Expected 1016 samples, got {len(output_data)}"
                
                # Verify first 16 samples are watermark on both channels
                assert np.any(output_data[:16, 0] != 0), "Left channel watermark should not be all zeros"
                assert np.any(output_data[:16, 1] != 0), "Right channel watermark should not be all zeros"
                
            finally:
                # Clean up
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
    
    def test_remove_watermark_samples_mono(self):
        """Test removing watermark samples from a mono audio file"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            
            input_path = input_file.name
            output_path = output_file.name
            
            try:
                # Create test audio file with watermark
                create_test_wav(input_path, duration_samples=1000, n_channels=1)
                
                # Add watermark
                watermarked_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                watermarked_path = watermarked_file.name
                watermarked_file.close()
                
                add_watermark_samples(input_path, watermarked_path)
                
                # Remove watermark
                remove_watermark_samples(watermarked_path, output_path)
                
                # Read output and verify
                output_data = read_wav_samples(output_path, n_channels=1)
                
                # Should have 16 fewer samples than watermarked file (1016 - 16 = 1000)
                assert len(output_data) == 1000, f"Expected 1000 samples, got {len(output_data)}"
                
                # Clean up watermarked file
                if os.path.exists(watermarked_path):
                    os.remove(watermarked_path)
                
            finally:
                # Clean up
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
    
    def test_remove_watermark_samples_stereo(self):
        """Test removing watermark samples from a stereo audio file"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            
            input_path = input_file.name
            output_path = output_file.name
            
            try:
                # Create test audio file with watermark
                create_test_wav(input_path, duration_samples=1000, n_channels=2)
                
                # Add watermark
                watermarked_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                watermarked_path = watermarked_file.name
                watermarked_file.close()
                
                add_watermark_samples(input_path, watermarked_path)
                
                # Remove watermark
                remove_watermark_samples(watermarked_path, output_path)
                
                # Read output and verify
                output_data = read_wav_samples(output_path, n_channels=2)
                
                # Should have 16 fewer samples than watermarked file (1016 - 16 = 1000)
                assert len(output_data) == 1000, f"Expected 1000 samples, got {len(output_data)}"
                
                # Clean up watermarked file
                if os.path.exists(watermarked_path):
                    os.remove(watermarked_path)
                
            finally:
                # Clean up
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
    
    def test_add_remove_add_different_watermark(self):
        """Test adding, removing, and adding a different watermark"""
        # Store original values
        original_db_values = app.DB_VALUES.copy()
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
            input_path = input_file.name
            
            try:
                # Create original audio file
                create_test_wav(input_path, duration_samples=1000, n_channels=1)
                original_data = read_wav_samples(input_path, n_channels=1)
                
                # Step 1: Add first watermark
                watermarked1_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                watermarked1_path = watermarked1_file.name
                watermarked1_file.close()
                
                add_watermark_samples(input_path, watermarked1_path)
                watermarked1_data = read_wav_samples(watermarked1_path, n_channels=1)
                
                # Verify watermark was added
                assert len(watermarked1_data) == 1016, "First watermark should add 16 samples"
                
                # Step 2: Remove watermark
                unwatermarked_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                unwatermarked_path = unwatermarked_file.name
                unwatermarked_file.close()
                
                remove_watermark_samples(watermarked1_path, unwatermarked_path)
                unwatermarked_data = read_wav_samples(unwatermarked_path, n_channels=1)
                
                # Verify watermark was removed
                assert len(unwatermarked_data) == 1000, "After removal, should have original length"
                
                # Step 3: Create a different pattern and add it
                # Modify DB_VALUES to create a different watermark pattern
                app.DB_VALUES = [-99, -90, -99, -90, -90, -90, -99, -90, -99, -90, -99, -90, -90, -99, -90, -99]
                
                # Add second (different) watermark
                watermarked2_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                watermarked2_path = watermarked2_file.name
                watermarked2_file.close()
                
                add_watermark_samples(unwatermarked_path, watermarked2_path)
                watermarked2_data = read_wav_samples(watermarked2_path, n_channels=1)
                
                # Verify second watermark was added
                assert len(watermarked2_data) == 1016, "Second watermark should add 16 samples"
                
                # Verify the two watermarks are different
                assert not np.array_equal(watermarked1_data[:16], watermarked2_data[:16]), \
                    "First and second watermarks should be different"
                
                # Clean up temporary files
                if os.path.exists(watermarked1_path):
                    os.remove(watermarked1_path)
                if os.path.exists(unwatermarked_path):
                    os.remove(unwatermarked_path)
                if os.path.exists(watermarked2_path):
                    os.remove(watermarked2_path)
                
            finally:
                # Restore original DB_VALUES
                app.DB_VALUES = original_db_values
                
                # Clean up
                if os.path.exists(input_path):
                    os.remove(input_path)
