const express = require('express');
const cors = require('cors');
const multer = require('multer');

const app = express();
const PORT = 5001;

// Configure multer for file uploads (memory storage for simplicity)
const upload = multer({ 
    storage: multer.memoryStorage(),
    limits: { fileSize: 500 * 1024 * 1024 } // 500MB limit
});

// Middleware
app.use(cors());
app.use(express.json());

// GET endpoint - returns service info
app.get('/api/llm', (req, res) => {
    res.json({
        service: 'LLM Service',
        version: '1.0.0',
        description: 'LLM service using LangChain.js',
        endpoints: {
            GET: '/api/llm - Get service information',
            POST: '/api/llm - Process audio file or JSON data'
        },
        library: {
            name: 'langchain',
            version: '1.0.1',
            description: 'Build context-aware reasoning applications'
        }
    });
});

// POST endpoint - accepts audio file or JSON
app.post('/api/llm', upload.single('audio'), async (req, res) => {
    try {
        let response = {
            success: true,
            timestamp: new Date().toISOString(),
            processed: null
        };

        // Check if an audio file was uploaded
        if (req.file) {
            response.processed = {
                type: 'audio',
                filename: req.file.originalname,
                size: req.file.size,
                mimetype: req.file.mimetype,
                message: 'Audio file received successfully'
            };
        } 
        // Check if JSON data was sent
        else if (req.body && Object.keys(req.body).length > 0) {
            response.processed = {
                type: 'json',
                data: req.body,
                message: 'JSON data received successfully'
            };
        } 
        else {
            return res.status(400).json({
                success: false,
                error: 'No audio file or JSON data provided'
            });
        }

        res.json(response);
    } catch (error) {
        console.error('Error processing request:', error);
        res.status(500).json({
            success: false,
            error: 'Error processing request',
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
    console.log(`Using LangChain.js for LLM capabilities`);
});
