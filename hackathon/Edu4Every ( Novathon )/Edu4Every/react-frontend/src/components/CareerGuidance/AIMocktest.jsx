import React, { useState } from 'react';

const AIMocktest = () => {
    const [jobRole, setJobRole] = useState('');
    const [experience, setExperience] = useState('');
    const [questions, setQuestions] = useState([]);
    const [error, setError] = useState('');

    const handleJobRoleChange = (e) => {
        setJobRole(e.target.value);
    };

    const handleExperienceChange = (e) => {
        setExperience(e.target.value);
    };

    const fetchQuestions = async () => {
        try {
            setError(''); // Reset error state before making the request
            const response = await fetch('https://5940-111-92-80-102.ngrok-free.app/ai-mock-test-genarate/generate-questions', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    job_role: jobRole,
                    experience: experience,
                }),
            });

            if (!response.ok) throw new Error('Failed to fetch questions');

            const data = await response.json();
            if (data && data.questions) {
                setQuestions(data.questions);
            } else {
                setError('No questions found for the given inputs.');
            }
        } catch (error) {
            console.error('Error fetching questions:', error);
            setError(error.message || 'Something went wrong. Please try again later.');
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (jobRole && experience) {
            fetchQuestions();
        } else {
            setError('Please provide both job role and experience.');
        }
    };

    return (
        <div className="max-w-md mx-auto p-4">
            <h1 className="text-2xl font-bold text-center mb-4">AI Mock Test Generator</h1>
            <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="jobRole">
                        Job Role
                    </label>
                    <input 
                        type="text" 
                        id="jobRole" 
                        value={jobRole} 
                        onChange={handleJobRoleChange} 
                        required 
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    />
                </div>
                <div className="mb-6">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="experience">
                        Experience
                    </label>
                    <input 
                        type="text" 
                        id="experience" 
                        value={experience} 
                        onChange={handleExperienceChange} 
                        required 
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    />
                </div>
                <button 
                    type="submit" 
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                >
                    Generate Questions
                </button>
            </form>

            {error && (
                <div className="text-red-500 text-sm mt-4">
                    <p>{error}</p>
                </div>
            )}

            {questions.length > 0 && (
                <div className="mt-4">
                    <h2 className="text-lg font-semibold">Generated Questions:</h2>
                    <ul className="list-disc pl-5">
                            <li className="my-2">{questions}</li>
                    </ul>
                </div>
            )}
        </div>
    );
};

export default AIMocktest;
