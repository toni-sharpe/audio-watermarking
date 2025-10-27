from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import numpy as np
import wave
import io
import os
import tempfile
from db_config import get_db_connection, release_db_connection
from audio_metadata import extract_and_save_metadata

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for React frontend
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max file size

# Enable CORS for the React frontend running on port 3000
# Only allow CORS on API endpoints that need cross-origin access
CORS(app, resources={
    r"/upload": {"origins": "http://localhost:3000", "expose_headers": ["Content-Disposition"]},
    r"/remove": {"origins": "http://localhost:3000", "expose_headers": ["Content-Disposition"]},
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
        if frame_rate not in [44100, 48000]:
            raise ValueError(f"Sample rate must be 44.1kHz (44100 Hz) or 48kHz (48000 Hz), got {frame_rate} Hz")
        if sample_width not in [2, 3]:
            raise ValueError(f"Sample width must be 2 bytes (16-bit) or 3 bytes (24-bit), got {sample_width} bytes")
        
        # Read all frames
        frames = wav_in.readframes(n_frames)
        
        # Handle different bit depths
        if sample_width == 2:
            audio_data = np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 3:
            # 24-bit audio: convert to int32
            audio_data = np.frombuffer(frames, dtype=np.uint8)
            # Reshape to groups of 3 bytes
            audio_data = audio_data.reshape(-1, 3)
            # Convert 24-bit to 32-bit signed integer
            audio_data = np.pad(audio_data, ((0, 0), (0, 1)), mode='constant')
            audio_data = audio_data.view(np.int32) >> 8
            audio_data = audio_data.flatten()
        
        # Reshape if stereo
        if n_channels == 2:
            audio_data = audio_data.reshape(-1, 2)
    
    # Create watermark samples with appropriate bit depth
    bit_depth = sample_width * 8
    watermark_samples = np.array([db_to_amplitude(db, bit_depth) for db in DB_VALUES], 
                                  dtype=np.int32 if sample_width == 3 else np.int16)
    
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
        
        # Convert back to bytes based on bit depth
        if sample_width == 2:
            wav_out.writeframes(watermarked_data.astype(np.int16).tobytes())
        elif sample_width == 3:
            # Convert 32-bit back to 24-bit
            data_32 = watermarked_data.astype(np.int32)
            # Shift left to put data in upper 24 bits
            data_32 = data_32 << 8
            # Convert to bytes and take only the 3 lower bytes
            data_bytes = data_32.tobytes()
            # Extract 24-bit values (skip the most significant byte of each 32-bit value)
            data_24 = np.frombuffer(data_bytes, dtype=np.uint8).reshape(-1, 4)[:, 1:4].tobytes()
            wav_out.writeframes(data_24)

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
        if frame_rate not in [44100, 48000]:
            raise ValueError(f"Sample rate must be 44.1kHz (44100 Hz) or 48kHz (48000 Hz), got {frame_rate} Hz")
        if sample_width not in [2, 3]:
            raise ValueError(f"Sample width must be 2 bytes (16-bit) or 3 bytes (24-bit), got {sample_width} bytes")
        
        # Read all frames
        frames = wav_in.readframes(n_frames)
        
        # Handle different bit depths
        if sample_width == 2:
            audio_data = np.frombuffer(frames, dtype=np.int16)
        elif sample_width == 3:
            # 24-bit audio: convert to int32
            audio_data = np.frombuffer(frames, dtype=np.uint8)
            # Reshape to groups of 3 bytes
            audio_data = audio_data.reshape(-1, 3)
            # Convert 24-bit to 32-bit signed integer
            audio_data = np.pad(audio_data, ((0, 0), (0, 1)), mode='constant')
            audio_data = audio_data.view(np.int32) >> 8
            audio_data = audio_data.flatten()
        
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
        
        # Convert back to bytes based on bit depth
        if sample_width == 2:
            wav_out.writeframes(unwatermarked_data.astype(np.int16).tobytes())
        elif sample_width == 3:
            # Convert 32-bit back to 24-bit
            data_32 = unwatermarked_data.astype(np.int32)
            # Shift left to put data in upper 24 bits
            data_32 = data_32 << 8
            # Convert to bytes and take only the 3 lower bytes
            data_bytes = data_32.tobytes()
            # Extract 24-bit values (skip the most significant byte of each 32-bit value)
            data_24 = np.frombuffer(data_bytes, dtype=np.uint8).reshape(-1, 4)[:, 1:4].tobytes()
            wav_out.writeframes(data_24)

@app.route('/api/nodes')
def get_nodes():
    """API endpoint to retrieve all nodes from the database"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query all nodes
        cur.execute("SELECT id, name FROM \"Node\" ORDER BY id;")
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

@app.route('/api/artists')
def get_artists():
    """API endpoint to retrieve all artists with their collective information"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query artists with their collective information
        cur.execute("""
            SELECT 
                n.id, 
                n.name,
                c.name as collective_name,
                ac."collectiveId"
            FROM "Node" n
            JOIN "Artist" a ON n.id = a."artistId"
            LEFT JOIN "ArtistCollective" ac ON a."artistId" = ac."artistId"
            LEFT JOIN "Node" c ON ac."collectiveId" = c.id
            WHERE n."nodeType" = 'artist'
            ORDER BY n.id;
        """)
        rows = cur.fetchall()
        
        # Format results as JSON
        artists = [{
            'id': row[0], 
            'name': row[1],
            'collective': row[2],
            'collectiveId': row[3]
        } for row in rows]
        
        cur.close()
        return jsonify(artists)
        
    except Exception as e:
        # Log the error for debugging (in production, use proper logging)
        # Don't expose detailed error messages to users
        return jsonify({'error': 'Failed to retrieve artists'}), 500
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
        
        # Create new filename with format: [original-name]--WM.[file-type]
        original_filename = file.filename
        name_parts = original_filename.rsplit('.', 1)
        if len(name_parts) == 2:
            base_name, extension = name_parts
            new_filename = f"{base_name}--WM.{extension}"
        else:
            new_filename = f"{original_filename}--WM"
        
        # Send the processed file back
        output_data.seek(0)
        return send_file(
            output_data,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=new_filename
        )
    
    except Exception as e:
        # Note: In production, avoid exposing detailed error messages to users
        # Use proper logging instead and return generic error messages
        return 'Error processing file. Please ensure the file is a valid WAV file (44.1kHz or 48kHz, 16-bit or 24-bit).', 500
    
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
        
        # Create new filename with format: [original-name]--NWM.[file-type]
        original_filename = file.filename
        name_parts = original_filename.rsplit('.', 1)
        if len(name_parts) == 2:
            base_name, extension = name_parts
            new_filename = f"{base_name}--NWM.{extension}"
        else:
            new_filename = f"{original_filename}--NWM"
        
        # Send the processed file back
        output_data.seek(0)
        return send_file(
            output_data,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=new_filename
        )
    
    except Exception as e:
        # Note: In production, avoid exposing detailed error messages to users
        # Use proper logging instead and return generic error messages
        return 'Error processing file. Please ensure the file is a valid WAV file (44.1kHz or 48kHz, 16-bit or 24-bit) with at least 16 samples.', 500
    
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass  # Ignore cleanup errors

@app.route('/api/metadata', methods=['POST'])
def extract_metadata():
    """Handle audio file upload and metadata extraction"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.wav'):
        return jsonify({'error': 'Only WAV files are supported'}), 400
    
    # Create temporary file for the uploaded audio
    input_fd, input_path = tempfile.mkstemp(suffix='.wav')
    
    # Determine output JSON filename
    original_filename = file.filename
    name_parts = original_filename.rsplit('.', 1)
    if len(name_parts) == 2:
        base_name, _ = name_parts
        json_filename = f"{base_name}-metadata.json"
    else:
        json_filename = f"{original_filename}-metadata.json"
    
    # Save JSON to root directory
    json_output_path = os.path.join(os.path.dirname(__file__), json_filename)
    
    try:
        # Close file descriptor and save uploaded file
        os.close(input_fd)
        file.save(input_path)
        
        # Extract metadata
        metadata = extract_and_save_metadata(input_path, json_output_path)
        
        # Return metadata in response
        return jsonify({
            'success': True,
            'metadata': metadata,
            'json_file': json_filename,
            'message': f'Metadata extracted and saved to {json_filename}'
        })
    
    except Exception as e:
        # Clean up JSON file if it was created
        if os.path.exists(json_output_path):
            try:
                os.remove(json_output_path)
            except:
                pass
        
        return jsonify({
            'success': False,
            'error': f'Error processing file: {str(e)}'
        }), 500
    
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
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
