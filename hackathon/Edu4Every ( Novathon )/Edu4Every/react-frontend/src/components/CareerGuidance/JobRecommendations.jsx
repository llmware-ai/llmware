import React, { useState } from 'react';
import axios from 'axios';
import { SearchIcon } from 'lucide-react';

const JobRecommendations = () => {
  const [formData, setFormData] = useState({
    favoriteProject: ''
  });

  const [responseData, setResponseData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    const payload = {
      questions: {
        "What are your core skills and strengths, and which ones do you enjoy using the most?": formData.skillsStrengths,
        "What kind of work environment and culture make you feel most productive and happy?": formData.workEnvironment,
        "What are your career goals and priorities for the next 3-5 years?": formData.careerGoals,
        "What motivates you the most at work—money, recognition, creativity, problem-solving, or something else?": formData.motivations,
        "Are there any industries or job types you're particularly passionate about or, conversely, want to avoid? Why?": formData.industriesInterest
      }
    };

    try {
      const response = await axios.post(
        'https://5940-111-92-80-102.ngrok-free.app/job_recommendation/recommend-jobs',
        payload,
        {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        }
      );

      setResponseData(response.data); // Assuming the response contains the job recommendations
    } catch (error) {
      console.error('Error occurred during the request:', error);
      setError('Failed to fetch job recommendations. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-white shadow-xl rounded-xl p-6">
        <div className="flex items-center mb-6">
          <SearchIcon className="w-10 h-10 text-blue-500 mr-4" />
          <h1 className="text-3xl font-bold text-gray-800">Job Recommendations</h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-700 font-medium mb-2">What are your core skills and strengths, and which ones do you enjoy using the most?</label>
            <textarea
              name="skillsStrengths"
              value={formData.skillsStrengths}
              onChange={handleInputChange}
              rows="4"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">What kind of work environment and culture make you feel most productive and happy?</label>
            <textarea
              name="workEnvironment"
              value={formData.workEnvironment}
              onChange={handleInputChange}
              rows="4"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">What are your career goals and priorities for the next 3-5 years?</label>
            <textarea
              name="careerGoals"
              value={formData.careerGoals}
              onChange={handleInputChange}
              rows="4"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">What motivates you the most at work—money, recognition, creativity, problem-solving, or something else?</label>
            <textarea
              name="motivations"
              value={formData.motivations}
              onChange={handleInputChange}
              rows="4"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Are there any industries or job types you're particularly passionate about or, conversely, want to avoid? Why?</label>
            <textarea
              name="industriesInterest"
              value={formData.industriesInterest}
              onChange={handleInputChange}
              rows="4"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors font-semibold flex items-center justify-center"
          >
            {isLoading ? (
              <div className="animate-spin mr-2">
                <SearchIcon className="w-5 h-5" />
              </div>
            ) : (
              "Submit and Get Career Guidance"
            )}
          </button>
        </form>

        {error && (
          <div className="mt-4 text-red-500 text-center">{error}</div>
        )}

        {responseData && (
          <div className="mt-6 space-y-4">
            <h2 className="text-xl font-bold text-gray-800">Job Recommendations</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {responseData.recommended_jobs.map((job, index) => (
                <div key={index} className="bg-white shadow-lg rounded-lg overflow-hidden">
                  <div className="p-6">
                    <h3 className="text-xl font-semibold text-gray-800">{job.title}</h3>
                    <a
                      href={job.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-4 text-blue-500 hover:underline"
                    >
                      Apply Now
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobRecommendations;
