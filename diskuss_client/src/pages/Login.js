import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import config from '../config';
import Spinner from './../components/Spinner';

const Login = ({setUser}) => {
  const navigate = useNavigate();

  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password) {
      alert('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${config.apiUrl}/api/auth/login`, form);
      localStorage.setItem('token', response.data.token);
      console.log('User login data:', response.data.user);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      setUser(response.data.user);
      setLoading(false);

      navigate('/chat');
    } catch (err) {
      setLoading(false);
      console.error('Error logging in:', err);
      alert(`Error logging in: ${err.response ? err.response.data.message : err.message}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md p-4 mx-auto">
      <h2 className="mb-4 text-2xl">Login</h2>
      <input name="username" onChange={handleChange} className="block w-full p-2 mb-2 border" placeholder="Username" />
      <input name="password" type="password" onChange={handleChange} className="block w-full p-2 mb-4 border" placeholder="Password" />
      <button type="submit" disabled={loading} className={`px-4 py-2 text-white ${loading ? 'bg-gray-500' : 'bg-green-500'} rounded`}>
        {loading ? <Spinner /> : 'Login'}
      </button>

      <p className="mt-4">
        Don't have an account? <a href="/register" className="text-blue-500">Register</a>
      </p>
    </form>
  )
}

export default Login;