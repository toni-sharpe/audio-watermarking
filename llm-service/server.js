const express = require('express');
const cors = require('cors');
const multer = require('multer');
const bodyParser = require('body-parser');
const path = require('path');
// LangChain integration - imported but not yet actively used
// The library is installed and ready for future LLM processing implementation
// const { ... } = require('langchain'); // Uncomment when implementing LLM features

const app = express();
const PORT = 5001;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 100 * 1024 * 1024, // 100MB limit
  },
});

// GET endpoint - returns service information
app.get('/api/llm', (req, res) => {
  res.json({
    service: 'LLM Service',
    version: '1.0.0',
    description: 'LLM service powered by LangChain',
    library: 'langchain',
    endpoints: {
      GET: '/api/llm - Get service information',
      POST: '/api/llm - Process audio file or JSON data with LLM'
    },
    status: 'running'
  });
});

// POST endpoint - processes audio file or JSON data
app.post('/api/llm', upload.single('audio'), async (req, res) => {
  try {
    let responseData = {
      success: true,
      timestamp: new Date().toISOString(),
      service: 'LLM Service',
    };

    // Check if file was uploaded
    if (req.file) {
      // Process audio file
      responseData.input_type = 'audio';
      responseData.file = {
        originalname: req.file.originalname,
        mimetype: req.file.mimetype,
        size: req.file.size,
      };
      responseData.message = 'Audio file received and ready for LLM processing';
      responseData.note = 'LLM processing integration can be added here';
    } 
    // Check if JSON data was sent
    else if (req.body && Object.keys(req.body).length > 0) {
      // Process JSON data
      responseData.input_type = 'json';
      responseData.data = req.body;
      responseData.message = 'JSON data received and ready for LLM processing';
      responseData.note = 'LLM processing integration can be added here';
    } 
    else {
      return res.status(400).json({
        success: false,
        error: 'No audio file or JSON data provided',
        message: 'Please provide either an audio file or JSON data'
      });
    }

    res.json(responseData);
  } catch (error) {
    console.error('Error processing request:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`LLM Service running on http://localhost:${PORT}`);
  console.log(`Powered by LangChain`);
  console.log(`Available endpoints:`);
  console.log(`  GET  http://localhost:${PORT}/api/llm`);
  console.log(`  POST http://localhost:${PORT}/api/llm`);
  console.log(`  GET  http://localhost:${PORT}/health`);
});

module.exports = app;
