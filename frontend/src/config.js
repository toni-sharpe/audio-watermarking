// API configuration
// Remove trailing slash to prevent double slashes in URLs
const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:5000').replace(/\/$/, '');

export { API_BASE_URL };
