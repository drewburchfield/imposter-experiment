/**
 * API configuration for development and production environments
 */

// In production (same origin), use relative URLs
// In development, use the local backend server
const isDev = import.meta.env.DEV;

export const API_BASE_URL = isDev ? 'http://localhost:8000' : '';

export const getApiUrl = (path: string) => `${API_BASE_URL}${path}`;
