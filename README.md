# Audio Watermarking

A simple web application for adding watermark samples to audio files.

## Features

- Upload WAV audio files (44.1kHz, 16-bit)
- Automatically adds 10 watermark samples at the beginning of the file
- Downloads the processed audio file
- Support for both mono and stereo audio files

## Requirements

- Python 3.7+
- Flask
- NumPy

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Upload a WAV file (44.1kHz, 16-bit) and the processed file will be automatically downloaded

## How it Works

The application adds 10 samples at the start of the audio file with the following amplitudes (in dB):
- -90dB, -98dB, -95dB, -90dB, -92dB, -92dB, -94dB, -99dB, -92dB, -91dB

These dB values are converted to 16-bit amplitude values using the formula:
```
amplitude = 10^(dB/20) × 32767
```

The watermark samples are prepended to the original audio data.

## Technical Details

- **Backend**: Python Flask server
- **Audio Processing**: NumPy for array manipulation, wave module for WAV file handling
- **Frontend**: Single HTML page with vanilla JavaScript
- **File Format**: WAV (44.1kHz, 16-bit, mono or stereo)
- **Max Upload Size**: 100 MB

## Security Notes

For production deployment:
- Use a production WSGI server (e.g., Gunicorn, uWSGI) instead of Flask's development server
- Set `debug=False` in the Flask app configuration
- Configure appropriate file upload limits
- Use HTTPS for secure file transfers
- Implement authentication if needed

## Example

To test the application with a sample file:

1. Create a test audio file (or use your own 44.1kHz 16-bit WAV file)
2. Upload through the web interface
3. The watermarked file will download automatically with prefix `watermarked_`

## Purpose

This is an initial experimental repository looking at CoPilot and how to work closely with the ML tool to accelerate my develop throughout a more complex, holistic and useful product.

## WIP

There is more to come here, I'm expecting all PRs to be raised by CoPilot based on my prompts.
