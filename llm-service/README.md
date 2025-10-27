# LLM Service

A Node.js service powered by LangChain.js for LLM capabilities.

## Features

- **LangChain.js Integration**: Uses LangChain.js (v1.0.1), one of the most popular and well-maintained JavaScript LLM libraries
- **GET Endpoint**: Returns service information and available endpoints
- **POST Endpoint**: Accepts audio files or JSON data for processing
- **CORS Enabled**: Configured for cross-origin requests from the React frontend

## Installation

```bash
cd llm-service
npm install
```

## Usage

Start the service:

```bash
npm start
```

The service will run on `http://localhost:5001`

## API Endpoints

### GET /api/llm

Returns service information, including available endpoints and library details.

**Response:**
```json
{
  "service": "LLM Service",
  "version": "1.0.0",
  "description": "LLM service using LangChain.js",
  "endpoints": {
    "GET": "/api/llm - Get service information",
    "POST": "/api/llm - Process audio file or JSON data"
  },
  "library": {
    "name": "langchain",
    "version": "1.0.1",
    "description": "Build context-aware reasoning applications"
  }
}
```

### POST /api/llm

Processes audio files or JSON data.

**Accepts:**
- Audio files (multipart/form-data with field name 'audio')
- JSON data (application/json)

**Example with audio file:**
```bash
curl -X POST -F "audio=@your-file.wav" http://localhost:5001/api/llm
```

**Example with JSON:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"key": "value", "example": "data"}' \
  http://localhost:5001/api/llm
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-10-27T09:33:11.361Z",
  "processed": {
    "type": "audio",
    "filename": "your-file.wav",
    "size": 12345,
    "mimetype": "audio/wav",
    "message": "Audio file received successfully"
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-27T09:33:11.361Z"
}
```

## About LangChain.js

LangChain.js is the official TypeScript/JavaScript library for building LLM applications. It was selected for this service because:

- **Popular**: 16,000+ stars on GitHub
- **Well-Maintained**: Active development with frequent updates
- **Many Contributors**: 2,800+ forks and large community
- **Comprehensive**: Full-featured framework for context-aware reasoning applications
- **Type-Safe**: Written in TypeScript with excellent type definitions

Learn more at: https://github.com/langchain-ai/langchainjs
