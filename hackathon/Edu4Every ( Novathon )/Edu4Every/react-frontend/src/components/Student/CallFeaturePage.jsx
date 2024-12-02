import React, { useState } from 'react';
import axios from 'axios';

const CallFeaturePage = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [callStatus, setCallStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [skill, setSkill] = useState('');
  const [level, setLevel] = useState('beginner');
  const [courseOutput, setCourseOutput] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const initiateCall = async (e) => {
    e.preventDefault();

    const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
    if (!phoneRegex.test(phoneNumber)) {
      setCallStatus('Please enter a valid phone number.');
      return;
    }

    setIsLoading(true);
    setCallStatus('');

    try {
      const response = await axios.post(
        'https://5940-111-92-80-102.ngrok-free.app/initiate-call/initiate-call',
        { number: phoneNumber },
        { headers: { accept: 'application/json', 'Content-Type': 'application/json' } }
      );
      setCallStatus(response.data.message || 'Call initiated successfully.');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        setCallStatus(
          error.response?.data?.message || 'Failed to initiate call. Please try again.'
        );
      } else {
        setCallStatus('An unexpected error occurred.');
      }
      console.error('Call initiation failed', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateCourse = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        'https://5940-111-92-80-102.ngrok-free.app/ai-learning-cource/generate-course',
        new URLSearchParams({ skill, level }),
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
      );
      setCourseOutput(response.data.course || 'Course generated successfully.');
    } catch (error) {
      console.error('Course generation failed', error);
      setCourseOutput('Failed to generate course. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-6 w-full">
      <div className="w-full max-w-4xl bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
          AI Course Generator & Call Assistant
        </h1>
        
        {/* AI Course Generator Section */}
        <div className="mb-10">
          <h2 className="text-2xl font-semibold text-gray-700 mb-6">
            Generate an AI-Powered Learning Course
          </h2>
          <form onSubmit={generateCourse} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Enter Skill (e.g., Python)"
              value={skill}
              onChange={(e) => setSkill(e.target.value)}
              className="col-span-1 w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              className="col-span-1 w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
            <button
              type="submit"
              className="col-span-1 sm:col-span-2 w-full py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors"
            >
              Generate Course
            </button>
          </form>

          {courseOutput && (
            <div className="mt-6 bg-gray-100 p-4 rounded-lg">
              <h3 className="font-bold text-lg mb-2">Generated Course:</h3>
              {courseOutput.split('\n').map((line, index) => (
                <p key={index} className="text-gray-700 mb-1">
                  {line}
                </p>
              ))}
            </div>
          )}
        </div>

        {/* AI Call Assistant Section */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-700 mb-6">AI Call Assistant</h2>
          <button
            onClick={() => setIsModalOpen(true)}
            className="w-full py-2 rounded-lg bg-green-500 text-white hover:bg-green-600 transition-colors"
          >
            Open Call Assistant
          </button>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white w-full max-w-lg rounded-lg p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 text-center">
              Enter Phone Number
            </h2>
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
            <button
              onClick={() => setIsModalOpen(false)}
              className="mt-4 w-full py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CallFeaturePage;
