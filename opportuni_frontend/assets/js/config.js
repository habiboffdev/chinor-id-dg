// Configuration file for Opportuni Platform

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Debug mode (set to false in production)
const DEBUG = true;

// Other configuration constants
const APP_NAME = 'Opportuni';
const VERSION = '1.0.0';

// Export for module usage (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        API_BASE_URL,
        DEBUG,
        APP_NAME,
        VERSION
    };
}
