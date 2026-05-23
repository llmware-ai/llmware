import React, { useState } from 'react';
import axios from 'axios';

const CallAIPage = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [callStatus, setCallStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const initiateCall = async (e) => {
    e.preventDefault(); // Prevent default form submission

    // Basic phone number validation
    const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
    if (!phoneRegex.test(phoneNumber)) {
      setCallStatus('Please enter a valid phone number');
      return;
    }

    setIsLoading(true);
    setCallStatus('');

    try {
      const response = await axios.post(
        'https://5940-111-92-80-102.ngrok-free.app/ai-roadmap/initiate-call',
        {
          number: phoneNumber,
        },
        {
          headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
          },
        }
      );
      
      setCallStatus(response.data.message || 'Call initiated successfully');
    } catch (error) {
      // Error handling
      if (axios.isAxiosError(error)) {
        setCallStatus(
          error.response?.data?.message || 'Failed to initiate call. Please try again.'
        );
      } else {
        setCallStatus('An unexpected error occurred');
      }
      console.error('Call initiation failed', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">AI Career Assistant</h2>
        
        <form onSubmit={initiateCall} className="space-y-4">
          <input
            type="tel"
            placeholder="Enter Phone Number (e.g., +1234567890)"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          
          {callStatus && (
            <div
              className={`p-3 rounded-lg text-center ${
                callStatus.includes('successfully') 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {callStatus}
            </div>
          )}
          
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-2 rounded-lg text-white transition-colors ${
              isLoading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-green-500 hover:bg-green-600'
            }`}
          >
            {isLoading ? 'Initiating Call...' : 'Initiate Call'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CallAIPage;