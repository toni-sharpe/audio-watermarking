import pytest
import tempfile
import os
from flask import Flask
from io import BytesIO
from app import app as flask_app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


def create_test_wav_bytes():
    """Create a simple test WAV file as bytes"""
    import wave
    import numpy as np
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create simple 44.1kHz 16-bit mono audio
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            audio_data = np.zeros(1000, dtype=np.int16)
            wav_file.writeframes(audio_data.tobytes())
        
        # Read the file as bytes
        with open(temp_path, 'rb') as f:
            wav_bytes = f.read()
        
        return wav_bytes
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


class TestFilenameFormat:
    """Test suite for filename format changes"""
    
    def test_upload_filename_format_wm(self, client):
        """Test that watermarked files have correct filename format"""
        wav_bytes = create_test_wav_bytes()
        
        # Upload file with specific name
        data = {
            'audio': (BytesIO(wav_bytes), 'test-audio.wav')
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 200
        assert response.content_type == 'audio/wav'
        
        # Check filename in Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition')
        assert content_disposition is not None
        assert 'test-audio--WM.wav' in content_disposition
        assert 'watermarked_' not in content_disposition
    
    def test_remove_filename_format_nwm(self, client):
        """Test that unwatermarked files have correct filename format"""
        wav_bytes = create_test_wav_bytes()
        
        # First, upload and watermark
        data = {
            'audio': (BytesIO(wav_bytes), 'sample-file.wav')
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        
        # Get the watermarked data
        watermarked_bytes = response.data
        
        # Now remove watermark
        data = {
            'audio': (BytesIO(watermarked_bytes), 'sample-file.wav')
        }
        
        response = client.post('/remove', data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 200
        assert response.content_type == 'audio/wav'
        
        # Check filename in Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition')
        assert content_disposition is not None
        assert 'sample-file--NWM.wav' in content_disposition
        assert 'unwatermarked_' not in content_disposition
    
    def test_upload_filename_with_multiple_dots(self, client):
        """Test filename format with multiple dots in filename"""
        wav_bytes = create_test_wav_bytes()
        
        # Upload file with multiple dots in name
        data = {
            'audio': (BytesIO(wav_bytes), 'my.test.audio.wav')
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        # Check response
        assert response.status_code == 200
        
        # Check filename - should preserve all but the last dot
        content_disposition = response.headers.get('Content-Disposition')
        assert content_disposition is not None
        assert 'my.test.audio--WM.wav' in content_disposition
    
    def test_upload_filename_without_extension(self, client):
        """Test filename format when file has no extension"""
        wav_bytes = create_test_wav_bytes()
        
        # This shouldn't happen in practice since we validate .wav extension,
        # but let's test the logic anyway by bypassing validation
        # Note: This test may not be practical given the .wav validation in the endpoint
        pass
