import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Check if user is already logged in (Session check)
    useEffect(() => {
        const checkSession = async () => {
            try {
                const { data } = await api.get('/auth/me');
                if (data.authenticated) {
                    setUser(data.user);
                }
            } catch (err) {
                console.log('No active session');
            } finally {
                setLoading(false);
            }
        };
        checkSession();
    }, []);

    const login = async (email, password) => {
        const { data } = await api.post('/auth/login', { email, password });
        setUser(data.user);
        return data;
    };

    const register = async (username, email, password, role) => {
        await api.post('/auth/register', { username, email, password, role });
    };

    const logout = async () => {
        await api.post('/auth/logout');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);