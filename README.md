# Audio Watermarking

A simple web application for adding watermark samples to audio files.

## Features

- Upload WAV audio files (44.1kHz or 48kHz, 16-bit or 24-bit)
- Automatically adds 16 watermark samples at the beginning of the file
- Downloads the processed audio file with format: `[original-name]--WM.wav` for watermarked files
- Remove watermark and download with format: `[original-name]--NWM.wav` for unwatermarked files
- Support for both mono and stereo audio files

## Requirements

- Python 3.9+
- Flask
- NumPy
- librosa (for audio metadata extraction)
- soundfile
- psycopg2-binary (for database operations)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Backend API Server

1. Start the Flask backend server:
   ```bash
   python app.py
   ```
   The backend API will run on `http://localhost:5000` and provides the following endpoints:
   - `POST /upload` - Add watermark to audio file
   - `POST /remove` - Remove watermark from audio file
   - `GET /api/nodes` - Retrieve all nodes from database
   - `GET /api/artists` - Retrieve all artists with collective information

### Frontend Application

2. Start the React frontend (in a separate terminal):
   ```bash
   cd frontend
   npm install  # First time only
   npm start
   ```
   The frontend will run on `http://localhost:3000`

3. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

4. Upload a WAV file (44.1kHz or 48kHz, 16-bit or 24-bit) and the processed file will be automatically downloaded

### Legacy HTML Interface

The original HTML interface (index.html, artists.html) is no longer served by the backend. Use the React frontend at `http://localhost:3000` instead.

## How it Works

The application adds 16 samples at the start of the audio file with amplitudes representing a binary pattern using two dB levels:
- **0 (low)**: -99dB
- **1 (high)**: -90dB

These dB values are converted to 16-bit amplitude values using the formula:
```
amplitude = 10^(dB/20) × 32767
```

The watermark samples are prepended to the original audio data.

## Technical Details

- **Backend**: Python Flask server
- **Audio Processing**: NumPy for array manipulation, wave module for WAV file handling
- **Frontend**: Single HTML page with vanilla JavaScript
- **File Format**: WAV (44.1kHz or 48kHz, 16-bit or 24-bit, mono or stereo)
- **Max Upload Size**: 500 MB
- **Download Format**: 
  - Watermarked: `[original-name]--WM.wav`
  - Unwatermarked: `[original-name]--NWM.wav`

## Security Notes

For production deployment:
- Use a production WSGI server (e.g., Gunicorn, uWSGI) instead of Flask's development server
- Set `debug=False` in the Flask app configuration
- Configure appropriate file upload limits
- Use HTTPS for secure file transfers
- Implement authentication if needed

## Example

To test the application with a sample file:

1. Create a test audio file (or use your own 44.1kHz or 48kHz, 16-bit or 24-bit WAV file)
2. Upload through the web interface
3. The watermarked file will download automatically with suffix `--WM`

## Purpose

This is an initial experimental repository looking at CoPilot and how to work closely with the ML tool to accelerate my develop throughout a more complex, holistic and useful product.

## Setup

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install flask numpy
```

## WIP

There is more to come here, I'm expecting all PRs to be raised by CoPilot based on my prompts.
