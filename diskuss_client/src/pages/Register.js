import React, { useState } from 'react';
import axios from 'axios';
import config from '../config';
import Spinner from './../components/Spinner';

const Register = () => {
  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    if (!form.username || !form.password) {
      alert('Please fill in all fields');
      setLoading(false);
      return;
    }
    
    try {
      const response = await axios.post(`${config.apiUrl}/api/auth/signup`, form);
      console.log('User registered successfully:', response.data);
      setLoading(false);
      window.location.href = '/login';
    } catch (error) {
      setLoading(false);
      console.error('Error registering user:', error);
      alert(`Error registering user: ${error.response ? error.response.data.message : error.message}`);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md p-4 mx-auto">
      <h2 className='mb-4 text-2xl' >Register</h2>
      <input name="username" onChange={handleChange} className="block w-full p-2 mb-2 border" placeholder="Username" />
      <input name="password" type="password" onChange={handleChange} className="block w-full p-2 mb-4 border" placeholder="Password" />

      <button type="submit" disabled={loading} className={`px-4 py-2 text-white ${loading ? 'bg-gray-500' : 'bg-green-500'} rounded`}>
        {loading ? <Spinner /> : 'Register'}
      </button>

      <p className="mt-4">
        Already have an account? <a href="/login" className="text-blue-500">Login</a>
      </p>
    </form>
  )
}

export default Register;