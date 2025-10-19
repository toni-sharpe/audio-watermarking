from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import numpy as np
import wave
import io
import os
import tempfile
from db_config import get_db_connection, release_db_connection

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for React frontend
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max file size

# Enable CORS for the React frontend running on port 3000
# Only allow CORS on API endpoints that need cross-origin access
CORS(app, resources={
    r"/upload": {"origins": "http://localhost:3000"},
    r"/remove": {"origins": "http://localhost:3000"},
    r"/api/*": {"origins": "http://localhost:3000"}
})

# dB values to amplitude conversion
# Formula: amplitude = 10^(dB/20)
# For 16-bit audio, we scale by 32767 (max value for signed 16-bit)
# Pattern represents binary 0s and 1s: 0 = -99dB (low), 1 = -90dB (high)
DB_VALUES = [-90, -99, -90, -90, -99, -99, -90, -99, -90, -99, -90, -90, -99, -90, -99, -99]
WATERMARK_SAMPLES = 16  # Number of samples in the watermark pattern

def db_to_amplitude(db, bit_depth=16):
    """Convert dB to amplitude value for the given bit depth"""
    max_amplitude = 2 ** (bit_depth - 1) - 1  # 32767 for 16-bit
    # Convert dB to linear scale and scale to bit depth
    linear = 10 ** (db / 20.0)
    amplitude = int(linear * max_amplitude)
    return amplitude

def add_watermark_samples(input_wav_path, output_wav_path):
    """Add 16 watermark samples at the beginning of the audio file"""
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

def remove_watermark_samples(input_wav_path, output_wav_path):
    """Remove the first 16 watermark samples from the beginning of the audio file"""
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
    
    # Remove first 16 samples (watermark)
    if len(audio_data) < WATERMARK_SAMPLES:
        raise ValueError(f"Audio file must have at least {WATERMARK_SAMPLES} samples to remove watermark")
    
    # Remove watermark samples from the beginning
    unwatermarked_data = audio_data[WATERMARK_SAMPLES:]
    
    # Write output WAV file
    with wave.open(output_wav_path, 'wb') as wav_out:
        wav_out.setnchannels(n_channels)
        wav_out.setsampwidth(sample_width)
        wav_out.setframerate(frame_rate)
        wav_out.writeframes(unwatermarked_data.astype(np.int16).tobytes())

@app.route('/')
def index():
    """Serve the HTML page"""
    return send_file('index.html')

@app.route('/artists')
def artists():
    """Serve the artists HTML page"""
    return send_file('artists.html')

@app.route('/api/nodes')
def get_nodes():
    """API endpoint to retrieve all nodes from the database"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query all nodes
        cur.execute("SELECT id, name FROM node ORDER BY id;")
        rows = cur.fetchall()
        
        # Format results as JSON
        nodes = [{'id': row[0], 'name': row[1]} for row in rows]
        
        cur.close()
        return jsonify(nodes)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

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
        # Note: In production, avoid exposing detailed error messages to users
        # Use proper logging instead and return generic error messages
        return 'Error processing file. Please ensure the file is a valid 44.1kHz 16-bit WAV file.', 500
    
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass  # Ignore cleanup errors

@app.route('/remove', methods=['POST'])
def remove_watermark():
    """Handle audio file upload and watermark removal"""
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
        remove_watermark_samples(input_path, output_path)
        
        # Read the processed file into memory
        with open(output_path, 'rb') as f:
            output_data = io.BytesIO(f.read())
        
        # Send the processed file back
        output_data.seek(0)
        return send_file(
            output_data,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=f'unwatermarked_{file.filename}'
        )
    
    except Exception as e:
        # Note: In production, avoid exposing detailed error messages to users
        # Use proper logging instead and return generic error messages
        return 'Error processing file. Please ensure the file is a valid 44.1kHz 16-bit WAV file with at least 16 samples.', 500
    
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
    # WARNING: This runs in debug mode for local development/testing only
    # For production deployment:
    # - Set debug=False or use environment variable FLASK_DEBUG=0
    # - Use a production WSGI server (e.g., gunicorn, uwsgi)
    # - Configure proper logging and error handling
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)
