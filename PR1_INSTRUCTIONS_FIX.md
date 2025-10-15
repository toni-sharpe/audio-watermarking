# Fix for PR #1 Instructions

## Problem

The instructions in PR #1 (copilot/add-audio-upload-feature) are incomplete. They tell users to:
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python app.py`

However, they don't mention that users need to:
1. Clone the repository first
2. Checkout the PR #1 branch (`copilot/add-audio-upload-feature`)
3. Be in the directory containing both `app.py` and `index.html`

## Root Cause

The Flask app (app.py) serves index.html from the same directory:
```python
@app.route('/')
def index():
    """Serve the HTML page"""
    return send_file('index.html')
```

If users don't have all the files in the same directory, the app will fail when they try to access `http://localhost:5000`.

## Solution

Update both README.md and QUICKSTART.md in PR #1 to include complete setup instructions:

### Updated README.md Installation Section

```markdown
## Installation

1. Clone this repository and checkout this PR branch:
   ```bash
   git clone https://github.com/toni-sharpe/audio-watermarking.git
   cd audio-watermarking
   git checkout copilot/add-audio-upload-feature
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Make sure you're in the repository directory (where app.py and index.html are located)

2. Start the server:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

4. Upload a WAV file (44.1kHz, 16-bit) and the processed file will be automatically downloaded
```

### Updated QUICKSTART.md Setup Section

```markdown
## Prerequisites

Before you start, you'll need:
- Python 3.7 or later installed
- Git (to clone the repository)

## Setup

1. **Clone the repository and checkout this PR branch**:
   ```bash
   git clone https://github.com/toni-sharpe/audio-watermarking.git
   cd audio-watermarking
   git checkout copilot/add-audio-upload-feature
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or on Ubuntu/Debian:
   ```bash
   sudo apt-get install python3-flask python3-numpy
   ```

## Running the Application

1. **Make sure you're in the repository directory** (where app.py and index.html are located)

2. **Start the server**:
   ```bash
   python app.py
   ```
```

### Add Troubleshooting Section to QUICKSTART.md

```markdown
## Troubleshooting

**Problem**: Server won't start or returns "File not found" error  
**Solution**: Make sure you're in the repository directory where both `app.py` and `index.html` are located. Both files must be in the same directory.

**Problem**: Upload fails with format error  
**Solution**: Ensure your WAV file is exactly 44.1kHz sample rate and 16-bit depth. You can check this with audio editing software or by using the test file creation script above.
```

## Commit Applied

The fix has been committed to branch `copilot/add-audio-upload-feature` with commit message:
"Fix setup instructions to include git checkout step"

This commit updates both README.md and QUICKSTART.md with the complete, working instructions.
