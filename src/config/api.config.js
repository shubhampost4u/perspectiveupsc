// src/config/api.config.js
const API_CONFIG = {
  DEV_API_URL: 'http://localhost:5000',
  PROD_API_URL: 'https://api.perspectiveupsc.com',
  getApiUrl: () => {
    return process.env.NODE_ENV === 'production' 
      ? API_CONFIG.PROD_API_URL 
      : API_CONFIG.DEV_API_URL;
  }
};