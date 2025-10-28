# Solution: ModuleNotFoundError: No module named 'librosa'

## Problem Summary

When trying to run the application with `python app.py`, the following error occurred:

```
Traceback (most recent call last):
  File "/Users/brainstem/Documents/desktop--250812/Find Work/audio-watermarking/app.py", line 9, in <module>
    from audio_metadata import extract_and_save_metadata
  File "/Users/brainstem/Documents/desktop--250812/Find Work/audio-watermarking/audio_metadata.py", line 6, in <module>
    import librosa
ModuleNotFoundError: No module named 'librosa'
```

## Root Cause

The error occurs because the required Python dependencies (including `librosa`) have not been installed yet. The `audio_metadata.py` module imports `librosa` on line 6, but the library is not available in the Python environment.

## Solution

Install all required dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- flask-cors (CORS support)
- numpy (numerical operations)
- psycopg2-binary (PostgreSQL database driver)
- librosa (audio analysis library) **← This is the missing module**
- soundfile (audio file I/O)

### Alternative: Using a Virtual Environment (Recommended)

For better dependency isolation, use a virtual environment:

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Verification

After installing the dependencies, you can verify the installation:

```bash
python -c "import librosa; print('librosa version:', librosa.__version__)"
```

Expected output:
```
librosa version: 0.11.0
```

You can also run the application:

```bash
python app.py
```

The server should start successfully on `http://localhost:5000`.

## Running Tests (Optional)

To verify everything is working correctly, you can run the test suite. Note that pytest is a development dependency and is not required to run the application:

```bash
pip install pytest  # pytest is needed for running tests but not for the application
pytest -v
```

All tests should pass.

## Why This Happened

The `requirements.txt` file contains all necessary dependencies, but they need to be explicitly installed before running the application. Python doesn't automatically install dependencies listed in `requirements.txt` - this is a manual step that must be performed after cloning the repository.

This is standard practice for Python projects:
1. Clone the repository
2. **Install dependencies** with `pip install -r requirements.txt`
3. Run the application

## Summary

✅ **Fixed**: Dependencies are now installed  
✅ **Verified**: Application imports work correctly  
✅ **Tested**: All existing tests pass  

The application is ready to run!
