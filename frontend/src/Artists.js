import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Artists.scss';
import { API_BASE_URL } from './config';

function Artists() {
    const [collectives, setCollectives] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCollectives();
    }, []);

    const fetchCollectives = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/collectives`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch collectives');
            }
            
            const data = await response.json();
            setCollectives(data);
            setLoading(false);
        } catch (err) {
            setError('Error loading collectives: ' + err.message);
            setLoading(false);
        }
    };

    const getTotalArtistCount = () => {
        // Count total artist entries (including duplicates if in multiple collectives)
        return collectives.reduce((sum, collective) => sum + collective.artists.length, 0);
    };

    const getUniqueArtistCount = () => {
        // Count unique artists
        const artistIds = new Set();
        collectives.forEach(collective => {
            collective.artists.forEach(artist => artistIds.add(artist.id));
        });
        return artistIds.size;
    };

    return (
        <div className="container">
            <div className="nav">
                <Link to="/">← Back to Audio Watermarking</Link>
            </div>
            
            <h1>Artists Database</h1>
            
            {loading && <div className="loading">Loading collectives...</div>}
            
            {error && <div className="error" style={{ display: 'block' }}>{error}</div>}
            
            {!loading && !error && (
                <>
                    <div className="collectives-list">
                        {collectives.length === 0 ? (
                            <div className="collective-item">No collectives found in database</div>
                        ) : (
                            collectives.map(collective => (
                                <div key={collective.id} className="collective-item">
                                    <h2 className="collective-name">
                                        {collective.name}
                                        <span className="collective-id"> (ID: {collective.id})</span>
                                    </h2>
                                    {collective.artists.length === 0 ? (
                                        <p className="no-artists">No artists in this collective</p>
                                    ) : (
                                        <ul className="artists-list">
                                            {collective.artists.map(artist => (
                                                <li key={`${collective.id}-${artist.id}`} className="artist-item">
                                                    <span className="artist-id">#{artist.id}</span>
                                                    <span className="artist-name">{artist.name}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                    
                    {collectives.length > 0 && (
                        <div className="count" style={{ display: 'block' }}>
                            Total collectives: {collectives.length}
                            <br />
                            Unique artists: {getUniqueArtistCount()}
                            <br />
                            Total artist listings: {getTotalArtistCount()} (includes artists in multiple collectives)
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default Artists;
