import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Llm.scss';

const LLM_API_URL = 'http://localhost:5001';

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
            let requestBody;
            let headers = {};
            
            if (inputType === 'audio') {
                const fileInput = document.getElementById('audioFile');
                
                if (!fileInput.files[0]) {
                    setMessage({ text: 'Please select an audio file', type: 'error' });
                    setLoading(false);
                    return;
                }
                
                requestBody = new FormData();
                requestBody.append('audio', fileInput.files[0]);
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
                
                requestBody = jsonInput;
                headers['Content-Type'] = 'application/json';
            }
            
            const fetchOptions = {
                method: 'POST',
                body: requestBody
            };
            
            if (Object.keys(headers).length > 0) {
                fetchOptions.headers = headers;
            }
            
            const apiResponse = await fetch(`${LLM_API_URL}/api/llm`, fetchOptions);
            
            const data = await apiResponse.json();
            
            if (apiResponse.ok && data.success) {
                setMessage({ 
                    text: 'Request processed successfully!', 
                    type: 'success' 
                });
                setResponse(data);
            } else {
                setMessage({ text: 'Error: ' + (data.error || data.message || 'Unknown error'), type: 'error' });
            }
        } catch (error) {
            setMessage({ text: 'Error: ' + error.message, type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="nav">
                <Link to="/">← Back to Audio Watermarking</Link>
            </div>
            
            <h1>LLM Service</h1>
            
            <div className="info">
                <p><strong>Service Information:</strong></p>
                <p>• Powered by LangChain</p>
                <p>• Accepts audio files or JSON data</p>
                <p>• Running on port 5001</p>
            </div>

            <div className="input-type-selector">
                <label>
                    <input 
                        type="radio" 
                        value="audio" 
                        checked={inputType === 'audio'} 
                        onChange={(e) => setInputType(e.target.value)}
                    />
                    Audio File
                </label>
                <label>
                    <input 
                        type="radio" 
                        value="json" 
                        checked={inputType === 'json'} 
                        onChange={(e) => setInputType(e.target.value)}
                    />
                    JSON Data
                </label>
            </div>

            <form className="upload-form" onSubmit={handleSubmit}>
                {inputType === 'audio' ? (
                    <div className="form-group">
                        <label htmlFor="audioFile">Select Audio File:</label>
                        <input type="file" id="audioFile" name="audio" accept="audio/*" />
                    </div>
                ) : (
                    <div className="form-group">
                        <label htmlFor="jsonInput">Enter JSON Data:</label>
                        <textarea 
                            id="jsonInput"
                            value={jsonInput}
                            onChange={(e) => setJsonInput(e.target.value)}
                            placeholder='{"key": "value"}'
                            rows="10"
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
