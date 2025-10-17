import React, { useState } from 'react';
import './Home.css';

function Home() {
    const [uploadMessage, setUploadMessage] = useState({ text: '', type: '' });
    const [removeMessage, setRemoveMessage] = useState({ text: '', type: '' });
    const [uploadLoading, setUploadLoading] = useState(false);
    const [removeLoading, setRemoveLoading] = useState(false);

    const handleUploadSubmit = async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('audioFile');
        
        if (!fileInput.files[0]) {
            setUploadMessage({ text: 'Please select a file', type: 'error' });
            return;
        }
        
        const formData = new FormData();
        formData.append('audio', fileInput.files[0]);
        
        setUploadLoading(true);
        setUploadMessage({ text: '', type: '' });
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'watermarked_' + fileInput.files[0].name;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                setUploadMessage({ 
                    text: 'Audio file processed successfully! Download started.', 
                    type: 'success' 
                });
                fileInput.value = '';
            } else {
                const error = await response.text();
                setUploadMessage({ text: 'Error: ' + error, type: 'error' });
            }
        } catch (error) {
            setUploadMessage({ text: 'Error: ' + error.message, type: 'error' });
        } finally {
            setUploadLoading(false);
        }
    };
    
    const handleRemoveSubmit = async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('audioFileRemove');
        
        if (!fileInput.files[0]) {
            setRemoveMessage({ text: 'Please select a file', type: 'error' });
            return;
        }
        
        const formData = new FormData();
        formData.append('audio', fileInput.files[0]);
        
        setRemoveLoading(true);
        setRemoveMessage({ text: '', type: '' });
        
        try {
            const response = await fetch('/remove', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'unwatermarked_' + fileInput.files[0].name;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                setRemoveMessage({ 
                    text: 'Watermark removed successfully! Download started.', 
                    type: 'success' 
                });
                fileInput.value = '';
            } else {
                const error = await response.text();
                setRemoveMessage({ text: 'Error: ' + error, type: 'error' });
            }
        } catch (error) {
            setRemoveMessage({ text: 'Error: ' + error.message, type: 'error' });
        } finally {
            setRemoveLoading(false);
        }
    };

    return (
        <div className="container">
            <h1>Audio Watermarking Tool</h1>
            
            <div className="info">
                <p><strong>Requirements:</strong></p>
                <p>• Audio file at 44.1kHz sample rate</p>
                <p>• 16-bit sample format</p>
                <p>• Supported formats: WAV</p>
            </div>

            <h2>Add Watermark</h2>
            <form className="upload-form" onSubmit={handleUploadSubmit}>
                <div className="form-group">
                    <label htmlFor="audioFile">Select Audio File:</label>
                    <input type="file" id="audioFile" name="audio" accept=".wav" required />
                </div>
                <button type="submit" disabled={uploadLoading}>
                    {uploadLoading ? 'Processing...' : 'Upload and Process'}
                </button>
            </form>

            {uploadMessage.text && (
                <div className={`message ${uploadMessage.type}`} style={{ display: 'block' }}>
                    {uploadMessage.text}
                </div>
            )}

            <h2>Remove Watermark</h2>
            <form className="upload-form" onSubmit={handleRemoveSubmit}>
                <div className="form-group">
                    <label htmlFor="audioFileRemove">Select Watermarked Audio File:</label>
                    <input type="file" id="audioFileRemove" name="audio" accept=".wav" required />
                </div>
                <button type="submit" className="remove-btn" disabled={removeLoading}>
                    {removeLoading ? 'Processing...' : 'Remove Watermark'}
                </button>
            </form>

            {removeMessage.text && (
                <div className={`message ${removeMessage.type}`} style={{ display: 'block' }}>
                    {removeMessage.text}
                </div>
            )}
        </div>
    );
}

export default Home;
