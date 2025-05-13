import './App.css';
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import config from './config';

import ChatLayout from './components/ChatLayout';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Spinner from './components/Spinner';

function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem('user'));
    const token = localStorage.getItem('token');

    if (userData) {
      setUser(userData);
      setAuthLoading(false);
    } else if (token) {
      axios.get(`${config.apiUrl}/api/diskuss/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(response => {
          const user = response.data.data;
          localStorage.setItem('user', JSON.stringify(user));
          setUser(user);
        })
        .catch(error => {
          console.error('Auth error:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        })
        .finally(() => {
          setAuthLoading(false); // <-- Make sure to end the loading state
        });
    } else {
      setAuthLoading(false);
    }
  }, []);

  const PrivateRoute = ({ children }) => {
    if (authLoading) return null;
    return user ? children : <Navigate to="/login" />;
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/chat" element={
          <PrivateRoute>
            <ChatLayout user={user} />
          </PrivateRoute>
        } />
        <Route path="/" element={<Home />} />
      </Routes>
    </Router>
  );
}

export default App;
