import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true, // Critical for sending cookies to Backend
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interceptor to handle session expiration globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // If backend returns 401 Unauthorized, verify if it's not the login page itself
            if (!window.location.pathname.includes('/login')) {
                // Optional: Trigger a logout action or redirect
                // window.location.href = '/login'; 
            }
        }
        return Promise.reject(error);
    }
);

export default api;