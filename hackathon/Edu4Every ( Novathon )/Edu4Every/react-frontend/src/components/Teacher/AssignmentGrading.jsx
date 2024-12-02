import React, { useState } from 'react';
import axios from 'axios';

const AssignmentGrading = () => {
  const [file, setFile] = useState(null);
  const [gradingText, setGradingText] = useState('');
  const [grade, setGrade] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Handle file upload
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // Handle grading text input
  const handleTextChange = (e) => {
    setGradingText(e.target.value);
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Check if both file and grading text are provided
    if (!file || !gradingText) {
      setError('Both file and grading text are required!');
      return;
    }

    setError('');
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file, file.name);
    formData.append('teacher_answer', gradingText);

    try {
      // Send request to the server
      const response = await axios.post(
        'https://5940-111-92-80-102.ngrok-free.app/correct-ai-assiagment/upload-and-process-pdf',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            accept: 'application/json',
          },
        }
      );
      
      // Set grade if the response is successful
      setGrade(response.data.mark);
      console.log('Assignment processed successfully:', response.data);
    } catch (err) {
      // Handle error during request
      setError('Failed to process the assignment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto mt-4 p-6 bg-white shadow-md rounded-lg">
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Assignment Grading</h1>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label
            htmlFor="file"
            className="block text-gray-700 font-medium mb-2"
          >
            Upload Assignment PDF:
          </label>
          <input
            type="file"
            id="file"
            onChange={handleFileChange}
            accept="application/pdf"
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
        </div>
        
        <div className="mb-4">
          <label
            htmlFor="gradingText"
            className="block text-gray-700 font-medium mb-2"
          >
            Grading Criteria:
          </label>
          <textarea
            id="gradingText"
            rows="4"
            value={gradingText}
            onChange={handleTextChange}
            className="w-full p-2 border rounded-md focus:outline-none focus:ring focus:ring-blue-300"
            placeholder="Enter grading criteria"
          ></textarea>
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-2 px-4 rounded-md text-white font-medium ${
            loading
              ? 'bg-blue-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>

      {/* Error message */}
      {error && (
        <p className="mt-4 text-red-500 text-sm font-medium">{error}</p>
      )}

      {/* Grading result */}
        {grade !== null && (
        <div className="mt-6 p-4 bg-green-100 border border-green-400 rounded-md">
            <h3 className="text-lg font-semibold text-green-700">
            Grading Result:
            </h3>
            <p className="text-green-800">Mark: {grade?.mark}</p> {/* Use grade?.mark to safely access the mark */}
        </div>
        )}

    </div>
  );
};

export default AssignmentGrading;
