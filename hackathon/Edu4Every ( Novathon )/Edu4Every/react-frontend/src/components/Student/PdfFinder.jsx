import React, { useState } from 'react';
import axios from 'axios';

const PdfFinder = () => {
  const [file, setFile] = useState(null); // To hold the PDF file
  const [query, setQuery] = useState(''); // To hold the query
  const [response, setResponse] = useState(''); // To hold the response from the backend
  const [loading, setLoading] = useState(false); // To show loading state while uploading

  // Handle file selection
  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  // Handle input change for the query
  const handleQueryChange = (event) => {
    setQuery(event.target.value);
  };

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!file || !query) {
      alert('Please upload a PDF and enter a query.');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('query', query);

    try {
      const response = await axios.post(
        'https://5940-111-92-80-102.ngrok-free.app/rag/upload-and-process-pdf',
        formData,
        {
          headers: {
            'accept': 'application/json',
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      // Handle the response from the backend (groq_response)
      setResponse(response.data.groq_response || 'No response from the server');
    } catch (error) {
      console.error('Error during file upload or query processing:', error);
      setResponse('Error processing your request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 mt-10 max-w-lg bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-center mb-4 text-gray-700">PDF Finder</h2>
      <form onSubmit={handleSubmit} encType="multipart/form-data" className="space-y-4">
        <div>
          <label htmlFor="file" className="block text-gray-600">Upload PDF:</label>
          <input
            type="file"
            id="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="mt-2 p-2 border border-gray-300 rounded w-full"
          />
        </div>
        <div>
          <label htmlFor="query" className="block text-gray-600">Enter your query:</label>
          <input
            type="text"
            id="query"
            value={query}
            onChange={handleQueryChange}
            placeholder="What is AI?"
            className="mt-2 p-2 border border-gray-300 rounded w-full"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full mt-4 p-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>

      {response && (
        <div className="mt-6 p-4 bg-gray-100 rounded border border-gray-300">
          <h3 className="text-lg font-semibold text-gray-700">Answer from PDF:</h3>
          <p className="mt-2 text-gray-600">{response}</p>
        </div>
      )}
    </div>
  );
};

export default PdfFinder;
