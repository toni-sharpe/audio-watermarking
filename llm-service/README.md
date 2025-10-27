# LLM Service

A Node.js service powered by LangChain that provides GET and POST endpoints for LLM processing.

## Features

- Built with Express.js
- Powered by LangChain (popular, well-forked JS LLM library)
- Accepts audio files or JSON data
- CORS enabled for frontend integration
- Runs on port 5001

## Installation

```bash
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

Returns service information.

**Example:**
```bash
curl http://localhost:5001/api/llm
```

### POST /api/llm

Processes audio file or JSON data.

**Example with JSON:**
```bash
curl -X POST http://localhost:5001/api/llm \
  -H "Content-Type: application/json" \
  -d '{"text": "test message"}'
```

**Example with audio file:**
```bash
curl -X POST http://localhost:5001/api/llm \
  -F "audio=@your-audio-file.wav"
```

### GET /health

Health check endpoint.

**Example:**
```bash
curl http://localhost:5001/health
```

## Dependencies

- **express**: Web framework
- **cors**: Enable CORS
- **multer**: Handle file uploads
- **body-parser**: Parse request bodies
- **langchain**: LLM framework
- **@langchain/core**: Core LangChain functionality

## Library Choice

This service uses **LangChain** as the LLM library because it is:
- Very popular (142k+ stars on GitHub)
- Well-maintained with many contributors
- Actively developed
- Designed specifically for building LLM applications
- Widely adopted in the industry
