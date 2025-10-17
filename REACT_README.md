# Audio Watermarking - React Frontend

This is the React frontend application for the Audio Watermarking tool.

## Prerequisites

- Node.js 14 or higher
- npm (comes with Node.js)
- Python 3.x with Flask backend running on port 5000

## Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

## Running the Application

### Development Mode

1. Make sure the Flask backend is running on `http://localhost:5000`

2. Start the React development server:
```bash
npm start
```

3. The application will automatically open in your browser at `http://localhost:3000`

### Production Build

To create a production-optimized build:

```bash
npm run build
```

This will create a `build` folder with optimized static files that can be served by any web server.

## Features

- **Audio Watermarking**: Upload WAV files to add watermarks
- **Watermark Removal**: Remove watermarks from previously watermarked files
- **Artists Database**: View artists from the backend database (requires database connection)
- **Responsive Design**: Works on desktop and mobile devices
- **Sass Styling**: Uses Sass for maintainable CSS

## Project Structure

```
frontend/
├── public/           # Static files
├── src/
│   ├── App.js       # Main application component with routing
│   ├── Home.js      # Home page component (watermarking functionality)
│   ├── Home.scss    # Styles for home page
│   ├── Artists.js   # Artists database page component
│   ├── Artists.scss # Styles for artists page
│   └── index.js     # Application entry point
└── package.json     # Project dependencies
```

## Technologies Used

- **React 19**: UI library
- **React Router DOM**: Client-side routing
- **Sass**: CSS preprocessor
- **Create React App**: Build tooling

## API Integration

The frontend communicates with the Flask backend through the following endpoints:

- `POST /upload` - Upload and add watermark to audio file
- `POST /remove` - Remove watermark from audio file
- `GET /api/nodes` - Fetch artists from database

The proxy is configured in `package.json` to forward API requests to `http://localhost:5000`.

## Available Scripts

- `npm start` - Run development server
- `npm run build` - Create production build
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (irreversible)

## Requirements

Audio files must meet the following requirements:
- Format: WAV
- Sample rate: 44.1kHz
- Bit depth: 16-bit
