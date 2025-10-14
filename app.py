from flask import Flask, request, send_file, jsonify
import numpy as np
import wave
import io
import os
import tempfile

app = Flask(__name__, static_folder='.')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max file size

# dB values to amplitude conversion
# Formula: amplitude = 10^(dB/20)
# For 16-bit audio, we scale by 32767 (max value for signed 16-bit)
DB_VALUES = [-90, -98, -95, -90, -92, -92, -94, -99, -92, -91]

def db_to_amplitude(db, bit_depth=16):
    """Convert dB to amplitude value for the given bit depth"""
    max_amplitude = 2 ** (bit_depth - 1) - 1  # 32767 for 16-bit
    # Convert dB to linear scale and scale to bit depth
    linear = 10 ** (db / 20.0)
    amplitude = int(linear * max_amplitude)
    return amplitude

def add_watermark_samples(input_wav_path, output_wav_path):
    """Add 10 watermark samples at the beginning of the audio file"""
    # Read the input WAV file
    with wave.open(input_wav_path, 'rb') as wav_in:
        # Get WAV parameters
        n_channels = wav_in.getnchannels()
        sample_width = wav_in.getsampwidth()
        frame_rate = wav_in.getframerate()
        n_frames = wav_in.getnframes()
        
        # Validate parameters
        if frame_rate != 44100:
            raise ValueError(f"Sample rate must be 44.1kHz (44100 Hz), got {frame_rate} Hz")
        if sample_width != 2:
            raise ValueError(f"Sample width must be 2 bytes (16-bit), got {sample_width} bytes")
        
        # Read all frames
        frames = wav_in.readframes(n_frames)
        audio_data = np.frombuffer(frames, dtype=np.int16)
        
        # Reshape if stereo
        if n_channels == 2:
            audio_data = audio_data.reshape(-1, 2)
    
    # Create watermark samples
    watermark_samples = np.array([db_to_amplitude(db) for db in DB_VALUES], dtype=np.int16)
    
    # For stereo, replicate watermark to both channels
    if n_channels == 2:
        watermark_samples = np.column_stack([watermark_samples, watermark_samples])
    
    # Reshape audio data for proper concatenation
    if n_channels == 2:
        watermark_reshaped = watermark_samples.reshape(-1, n_channels)
        audio_reshaped = audio_data.reshape(-1, n_channels)
    else:
        watermark_reshaped = watermark_samples.reshape(-1, 1)
        audio_reshaped = audio_data.reshape(-1, 1)
    
    # Prepend watermark samples to audio data
    watermarked_data = np.vstack([watermark_reshaped, audio_reshaped])
    
    # Write output WAV file
    with wave.open(output_wav_path, 'wb') as wav_out:
        wav_out.setnchannels(n_channels)
        wav_out.setsampwidth(sample_width)
        wav_out.setframerate(frame_rate)
        wav_out.writeframes(watermarked_data.astype(np.int16).tobytes())

@app.route('/')
def index():
    """Serve the HTML page"""
    return send_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle audio file upload and watermarking"""
    if 'audio' not in request.files:
        return 'No audio file provided', 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return 'No file selected', 400
    
    if not file.filename.lower().endswith('.wav'):
        return 'Only WAV files are supported', 400
    
    # Create temporary files
    input_fd, input_path = tempfile.mkstemp(suffix='.wav')
    output_fd, output_path = tempfile.mkstemp(suffix='.wav')
    
    try:
        # Close file descriptors and save uploaded file
        os.close(input_fd)
        os.close(output_fd)
        
        file.save(input_path)
        
        # Process the audio file
        add_watermark_samples(input_path, output_path)
        
        # Read the processed file into memory
        with open(output_path, 'rb') as f:
            output_data = io.BytesIO(f.read())
        
        # Send the processed file back
        output_data.seek(0)
        return send_file(
            output_data,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=f'watermarked_{file.filename}'
        )
    
    except Exception as e:
        return f'Error processing file: {str(e)}', 500
    
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass  # Ignore cleanup errors

if __name__ == '__main__':
    # For production, use a proper WSGI server and set debug=False
    app.run(debug=True, host='127.0.0.1', port=5000)
