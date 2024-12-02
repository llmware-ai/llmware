import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Eye, EyeOff, Lock, User } from 'lucide-react';

const CareerGuidanceLogin = () => {
  const [unique_id, setUniqueId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    if (unique_id && password) {
      try {
        const response = await axios.post(
          'https://5940-111-92-80-102.ngrok-free.app/carrier_guidance/login', 
          {
            unique_id, 
            password
          },
          {
            headers: {
              'accept': 'application/json',
              'Content-Type': 'application/json'
            }
          }
        );

        
        if (response.data.name) {
          localStorage.setItem('userRole', 'career-guidance');
          localStorage.setItem('studentName', response.data.name);
          localStorage.setItem('Id', unique_id);
          navigate('/dashboard/career-guidance-dashboard');
        } else {
          setError('Invalid credentials. Please try again.');
        }
      } catch (err) {
        setError('An error occurred. Please try again later.');
      }
    } else {
      setError('Please enter valid credentials.');
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-100 to-purple-100 relative overflow-hidden"
    style={{ backgroundImage: "url('https://c0.wallpaperflare.com/preview/274/250/540/career-success-path-stair.jpg')", backgroundSize: "cover", opacity: 0.8 }}
    >
      <div className="absolute inset-0 opacity-10 bg-[size:100px_100px] bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)]"></div>
      
      {/* Glassmorphic login container */}
      <div className="relative w-full max-w-md mx-4">
        <div className="bg-white/30 backdrop-blur-lg border border-white/20 shadow-2xl rounded-2xl p-8 relative overflow-hidden">
          {/* Subtle background glow */}
          <div className="absolute -top-10 -right-10 w-32 h-32 bg-blue-300 rounded-full opacity-30 blur-3xl"></div>
          <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-purple-300 rounded-full opacity-30 blur-3xl"></div>
          
          <h2 className="text-3xl font-bold text-center mb-6 text-gray-800 relative z-10">
            Career Guidance
          </h2>

          {/* Error message display */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4 text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4 relative z-10">
            <div className="relative">
              <label htmlFor="uniqueId" className="block text-gray-700 font-medium mb-2">
                Unique ID
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                <input
                  type="text"
                  id="uniqueId"
                  value={unique_id}
                  onChange={(e) => setUniqueId(e.target.value)}
                  className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/70"
                  placeholder="Enter your unique ID"
                  required
                />
              </div>
            </div>
            <div className="relative">
              <label htmlFor="password" className="block text-gray-700 font-medium mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                <input
                  type={showPassword ? "text" : "password"}
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white/70"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 focus:outline-none"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold shadow-md hover:shadow-lg"
            >
              Login
            </button>
          </form>

          {/* Forgot Password Link */}
          <div className="text-center mt-4">
            <a 
              href="/forgot-password" 
              className="text-blue-600 hover:text-blue-800 text-sm transition-colors"
            >
              Forgot Password?
            </a>
          </div>
        </div>

        {/* Decorative element */}
        <div className="mt-4 text-center text-gray-600 text-sm">
          © {new Date().getFullYear()} Career Guidance Portal. All rights reserved.
        </div>
      </div>
    </div>
  );
};

export default CareerGuidanceLogin;
