// write a simple home page with buttons to register and login. also it should fit entire screen. name of app is Diskuss

import React from 'react';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  const handleRegister = () => {
    navigate('/register');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="mb-8 text-4xl font-bold">Diskuss</h1>
      <div className="flex space-x-4">
        <button onClick={handleRegister} className="px-4 py-2 text-white bg-blue-500 rounded">
          Register
        </button>
        <button onClick={handleLogin} className="px-4 py-2 text-white bg-green-500 rounded">
          Login
        </button>
      </div>
    </div>
  );
};

export default Home;