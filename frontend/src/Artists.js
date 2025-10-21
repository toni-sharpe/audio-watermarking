import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Artists.scss';

function Artists() {
    const [artists, setArtists] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchArtists();
    }, []);

    const fetchArtists = async () => {
        try {
            const response = await fetch('/api/artists');
            
            if (!response.ok) {
                throw new Error('Failed to fetch artists');
            }
            
            const data = await response.json();
            setArtists(data);
            setLoading(false);
        } catch (err) {
            setError('Error loading artists: ' + err.message);
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="nav">
                <Link to="/">← Back to Audio Watermarking</Link>
            </div>
            
            <h1>Artists Database</h1>
            
            {loading && <div className="loading">Loading artists...</div>}
            
            {error && <div className="error" style={{ display: 'block' }}>{error}</div>}
            
            {!loading && !error && (
                <>
                    <ul className="artists-list">
                        {artists.length === 0 ? (
                            <li className="artist-item">No artists found in database</li>
                        ) : (
                            artists.map(artist => (
                                <li key={artist.id} className="artist-item">
                                    <span className="artist-id">#{artist.id}</span>
                                    <span className="artist-name">{artist.name}</span>
                                    {artist.collective && (
                                        <span className="artist-collective">
                                            {artist.collective}
                                        </span>
                                    )}
                                </li>
                            ))
                        )}
                    </ul>
                    
                    {artists.length > 0 && (
                        <div className="count" style={{ display: 'block' }}>
                            Total artists: {artists.length}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default Artists;
