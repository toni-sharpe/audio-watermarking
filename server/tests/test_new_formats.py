import pytest
import numpy as np
import wave
import tempfile
import os
from app import add_watermark_samples, remove_watermark_samples


def create_test_wav(filename, duration_samples=1000, n_channels=1, sample_rate=44100, sample_width=2):
    """Helper function to create a test WAV file"""
    # Generate silent audio data
    if sample_width == 2:
        audio_data = np.zeros(duration_samples, dtype=np.int16)
    elif sample_width == 3:
        # For 24-bit, we'll create int32 data that will be converted
        audio_data = np.zeros(duration_samples, dtype=np.int32)
    
    if n_channels == 2:
        audio_data = np.column_stack([audio_data, audio_data])
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        
        if sample_width == 2:
            wav_file.writeframes(audio_data.astype(np.int16).tobytes())
        elif sample_width == 3:
            # Convert 32-bit to 24-bit
            data_32 = audio_data.astype(np.int32)
            data_32 = data_32 << 8
            data_bytes = data_32.tobytes()
            data_24 = np.frombuffer(data_bytes, dtype=np.uint8).reshape(-1, 4)[:, 1:4].tobytes()
            wav_file.writeframes(data_24)


def read_wav_samples(filename, n_channels=1, sample_width=2):
    """Helper function to read samples from a WAV file"""
    with wave.open(filename, 'rb') as wav_file:
        n_frames = wav_file.getnframes()
        frames = wav_file.readframes(n_frames)
        
        if sample_width == 2:
            audio_data = np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 3:
            audio_data = np.frombuffer(frames, dtype=np.uint8)
            audio_data = audio_data.reshape(-1, 3)
            audio_data = np.pad(audio_data, ((0, 0), (0, 1)), mode='constant')
            audio_data = audio_data.view(np.int32) >> 8
            audio_data = audio_data.flatten()
        
        if n_channels == 2:
            audio_data = audio_data.reshape(-1, 2)
    
    return audio_data


class TestNewFormats:
    """Test suite for new sample rates and bit depths"""
    
    def test_add_watermark_48khz_16bit_mono(self):
        """Test adding watermark to 48kHz 16-bit mono audio"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            
            input_path = input_file.name
            output_path = output_file.name
            
            try:
                # Create test audio file at 48kHz
                create_test_wav(input_path, duration_samples=1000, n_channels=1, sample_rate=48000, sample_width=2)
                
                # Add watermark
                add_watermark_samples(input_path, output_path)
                
                # Read output and verify
                output_data = read_wav_samples(output_path, n_channels=1, sample_width=2)
                
                # Should have 16 more samples than input
                assert len(output_data) == 1016, f"Expected 1016 samples, got {len(output_data)}"
                
                # Verify first 16 samples are watermark
                assert np.any(output_data[:16] != 0), "Watermark samples should not be all zeros"
                
            finally:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
    
    def test_add_watermark_44khz_24bit_mono(self):
        """Test adding watermark to 44.1kHz 24-bit mono audio"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            
            input_path = input_file.name
            output_path = output_file.name
            
            try:
                # Create test audio file with 24-bit depth
                create_test_wav(input_path, duration_samples=1000, n_channels=1, sample_rate=44100, sample_width=3)
                
                # Add watermark
                add_watermark_samples(input_path, output_path)
                
                # Read output and verify
                output_data = read_wav_samples(output_path, n_channels=1, sample_width=3)
                
                # Should have 16 more samples than input
                assert len(output_data) == 1016, f"Expected 1016 samples, got {len(output_data)}"
                
                # Verify first 16 samples are watermark
                assert np.any(output_data[:16] != 0), "Watermark samples should not be all zeros"
                
            finally:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
    
    def test_add_watermark_48khz_24bit_stereo(self):
        """Test adding watermark to 48kHz 24-bit stereo audio"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            
            input_path = input_file.name
            output_path = output_file.name
            
            try:
                # Create test audio file with 48kHz and 24-bit depth
                create_test_wav(input_path, duration_samples=1000, n_channels=2, sample_rate=48000, sample_width=3)
                
                # Add watermark
                add_watermark_samples(input_path, output_path)
                
                # Read output and verify
                output_data = read_wav_samples(output_path, n_channels=2, sample_width=3)
                
                # Should have 16 more samples than input
                assert len(output_data) == 1016, f"Expected 1016 samples, got {len(output_data)}"
                
                # Verify first 16 samples are watermark on both channels
                assert np.any(output_data[:16, 0] != 0), "Left channel watermark should not be all zeros"
                assert np.any(output_data[:16, 1] != 0), "Right channel watermark should not be all zeros"
                
            finally:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
    
    def test_remove_watermark_48khz_24bit(self):
        """Test removing watermark from 48kHz 24-bit audio"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            
            input_path = input_file.name
            output_path = output_file.name
            
            try:
                # Create test audio file
                create_test_wav(input_path, duration_samples=1000, n_channels=1, sample_rate=48000, sample_width=3)
                
                # Add watermark
                watermarked_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                watermarked_path = watermarked_file.name
                watermarked_file.close()
                
                add_watermark_samples(input_path, watermarked_path)
                
                # Remove watermark
                remove_watermark_samples(watermarked_path, output_path)
                
                # Read output and verify
                output_data = read_wav_samples(output_path, n_channels=1, sample_width=3)
                
                # Should have original length
                assert len(output_data) == 1000, f"Expected 1000 samples, got {len(output_data)}"
                
                # Clean up watermarked file
                if os.path.exists(watermarked_path):
                    os.remove(watermarked_path)
                
            finally:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
    
    def test_reject_unsupported_sample_rate(self):
        """Test that unsupported sample rates are rejected"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            
            input_path = input_file.name
            output_path = output_file.name
            
            try:
                # Create test audio file with unsupported sample rate
                create_test_wav(input_path, duration_samples=1000, n_channels=1, sample_rate=22050, sample_width=2)
                
                # Try to add watermark - should raise ValueError
                with pytest.raises(ValueError, match="Sample rate must be"):
                    add_watermark_samples(input_path, output_path)
                
            finally:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
