import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Llm.scss';

const LLM_SERVICE_URL = 'http://localhost:5001';

function Llm() {
    const [message, setMessage] = useState({ text: '', type: '' });
    const [loading, setLoading] = useState(false);
    const [inputType, setInputType] = useState('audio'); // 'audio' or 'json'
    const [jsonInput, setJsonInput] = useState('');
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        setLoading(true);
        setMessage({ text: '', type: '' });
        setResponse(null);
        
        try {
            let fetchOptions = {
                method: 'POST',
            };

            if (inputType === 'audio') {
                const fileInput = document.getElementById('audioFile');
                
                if (!fileInput.files[0]) {
                    setMessage({ text: 'Please select a file', type: 'error' });
                    setLoading(false);
                    return;
                }
                
                const formData = new FormData();
                formData.append('audio', fileInput.files[0]);
                fetchOptions.body = formData;
            } else {
                // JSON input
                if (!jsonInput.trim()) {
                    setMessage({ text: 'Please enter JSON data', type: 'error' });
                    setLoading(false);
                    return;
                }

                try {
                    JSON.parse(jsonInput); // Validate JSON
                } catch (err) {
                    setMessage({ text: 'Invalid JSON format', type: 'error' });
                    setLoading(false);
                    return;
                }

                fetchOptions.headers = {
                    'Content-Type': 'application/json'
                };
                fetchOptions.body = jsonInput;
            }
            
            const apiResponse = await fetch(`${LLM_SERVICE_URL}/api/llm`, fetchOptions);
            
            if (apiResponse.ok) {
                const data = await apiResponse.json();
                setResponse(data);
                setMessage({ 
                    text: 'Request processed successfully!', 
                    type: 'success' 
                });
            } else {
                const error = await apiResponse.json();
                setMessage({ text: 'Error: ' + (error.error || 'Unknown error'), type: 'error' });
            }
        } catch (error) {
            setMessage({ text: 'Error: ' + error.message, type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <h1>LLM Service Interface</h1>
            
            <div className="nav" style={{ textAlign: 'center', marginBottom: '20px' }}>
                <Link to="/" style={{ color: '#4CAF50', textDecoration: 'none', fontSize: '14px' }}>
                    ← Back to Audio Watermarking
                </Link>
                {' | '}
                <Link to="/artists" style={{ color: '#4CAF50', textDecoration: 'none', fontSize: '14px' }}>
                    View Artists Database →
                </Link>
            </div>
            
            <div className="info">
                <p><strong>LLM Service powered by LangChain.js</strong></p>
                <p>• Submit audio files or JSON data</p>
                <p>• Service running on port 5001</p>
                <p>• Maximum file size: 500MB</p>
            </div>

            <div className="input-type-selector">
                <label>
                    <input 
                        type="radio" 
                        name="inputType" 
                        value="audio" 
                        checked={inputType === 'audio'}
                        onChange={(e) => setInputType(e.target.value)}
                    />
                    {' '}Audio File
                </label>
                <label style={{ marginLeft: '20px' }}>
                    <input 
                        type="radio" 
                        name="inputType" 
                        value="json" 
                        checked={inputType === 'json'}
                        onChange={(e) => setInputType(e.target.value)}
                    />
                    {' '}JSON Data
                </label>
            </div>

            <h2>Submit Data to LLM Service</h2>
            <form className="upload-form" onSubmit={handleSubmit}>
                {inputType === 'audio' ? (
                    <div className="form-group">
                        <label htmlFor="audioFile">Select Audio File:</label>
                        <input type="file" id="audioFile" name="audio" accept=".wav,.mp3,.flac" />
                    </div>
                ) : (
                    <div className="form-group">
                        <label htmlFor="jsonInput">Enter JSON Data:</label>
                        <textarea
                            id="jsonInput"
                            name="jsonInput"
                            value={jsonInput}
                            onChange={(e) => setJsonInput(e.target.value)}
                            placeholder='{"key": "value", "example": "data"}'
                            rows="8"
                            style={{
                                width: '100%',
                                padding: '10px',
                                border: '2px solid #ddd',
                                borderRadius: '4px',
                                fontFamily: 'monospace',
                                fontSize: '14px'
                            }}
                        />
                    </div>
                )}
                <button type="submit" disabled={loading}>
                    {loading ? 'Processing...' : 'Submit to LLM Service'}
                </button>
            </form>

            {message.text && (
                <div className={`message ${message.type}`} style={{ display: 'block' }}>
                    {message.text}
                </div>
            )}

            {response && (
                <div className="response-container">
                    <h3>Response:</h3>
                    <pre>{JSON.stringify(response, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}

export default Llm;
