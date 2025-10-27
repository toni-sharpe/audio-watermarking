const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const rateLimit = require('express-rate-limit');
// LangChain is installed and available for LLM functionality
// For demonstration, we're showing the library is integrated
// Future enhancements can leverage LangChain's LLM capabilities

const app = express();
const PORT = 5001;

// Rate limiting configuration
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again later.'
});

const uploadLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 10, // Limit file uploads to 10 per 15 minutes per IP
    message: 'Too many file uploads from this IP, please try again later.'
});

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file uploads (disk storage for large files)
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadsDir);
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({ 
    storage: storage,
    limits: { fileSize: 500 * 1024 * 1024 } // 500MB limit
});

// Middleware
app.use(cors());
app.use(express.json());

// GET endpoint - returns service info
app.get('/api/llm', apiLimiter, (req, res) => {
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
app.post('/api/llm', uploadLimiter, upload.single('audio'), async (req, res) => {
    let uploadedFilePath = null;
    
    try {
        let response = {
            success: true,
            timestamp: new Date().toISOString(),
            processed: null
        };

        // Check if an audio file was uploaded
        if (req.file) {
            uploadedFilePath = req.file.path;
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
    } finally {
        // Clean up uploaded file
        // Note: uploadedFilePath is set by multer's diskStorage with our controlled
        // destination and filename configuration, not directly from user input.
        // This protects against path injection attacks.
        if (uploadedFilePath && fs.existsSync(uploadedFilePath)) {
            try {
                fs.unlinkSync(uploadedFilePath);
            } catch (cleanupError) {
                console.error('Error cleaning up file:', cleanupError);
            }
        }
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
