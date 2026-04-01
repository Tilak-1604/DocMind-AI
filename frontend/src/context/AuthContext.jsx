import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [status, setStatus] = useState('loading'); // 'loading' | 'authenticated' | 'unauthenticated'

    useEffect(() => {
        const validateToken = async () => {
            if (token) {
                try {
                    // VERIFY: Professional check with backend on load
                    const response = await axios.get('/auth/validate', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    setUser(response.data);
                    setStatus('authenticated');
                } catch (err) {
                    console.error("Token verification failed", err);
                    logout();
                    setStatus('unauthenticated');
                }
            } else {
                setStatus('unauthenticated');
            }
        };
        validateToken();
    }, [token]);

    const login = async (email, password) => {
        setStatus('loading');
        try {
            const response = await axios.post('/auth/login', { email, password });
            const { token, user } = response.data;
            setToken(token);
            setUser(user);
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(user));
            setStatus('authenticated');
            return user;
        } catch (err) {
            setStatus('unauthenticated');
            throw err;
        }
    };

    const register = async (email, password, name) => {
        setStatus('loading');
        try {
            const response = await axios.post('/auth/re' + 'gister', { email, password, name });
            const { token, user } = response.data;
            setToken(token);
            setUser(user);
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(user));
            setStatus('authenticated');
            return user;
        } catch (err) {
            setStatus('unauthenticated');
            throw err;
        }
    };

    const googleLogin = async (idToken) => {
        setStatus('loading');
        try {
            const response = await axios.post('/auth/google', { idToken });
            const { token, user } = response.data;
            setToken(token);
            setUser(user);
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(user));
            setStatus('authenticated');
            return user;
        } catch (err) {
            setStatus('unauthenticated');
            throw err;
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setStatus('unauthenticated');
    };

    return (
        <AuthContext.Provider value={{ user, token, status, login, register, googleLogin, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
