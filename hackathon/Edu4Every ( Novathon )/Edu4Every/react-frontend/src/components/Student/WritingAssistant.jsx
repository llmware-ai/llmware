import React, { useState } from 'react';
import axios from 'axios';
import jsPDF from 'jspdf';
import {  FaPen } from 'react-icons/fa';

const WritingAssistant = () => {
  const [userInput, setUserInput] = useState('');
  const [suggestions, setSuggestions] = useState([]); // Change to an array for multiple suggestions

  // Function to handle text input
  const handleInputChange = (e) => {
    const value = e.target.value;
    setUserInput(value);

    // Check if the last character is a period
    if (value.trim().endsWith('.')) {
      processText(value.slice(0, -1)); // Call processText without the period
    }
  };

  // Function to process text (send to backend)
  const processText = async (textBeforePeriod) => {
    try {
      const response = await axios.post(
        `https://5940-111-92-80-102.ngrok-free.app/writing_assistant/check-sentence`,
        null,
        {
          params: { sentence: textBeforePeriod },
          headers: { accept: 'application/json' },
        }
      );
      console.log('Suggestion received:', response.data);
      if (response.data && response.data.suggestions) {
        setSuggestions(response.data.suggestions); // Update to set an array of suggestions
      }
    } catch (error) {
      console.error('Error fetching suggestion:', error);
    }
  };

  // Function to download content as PDF remains unchanged
  const downloadPDF = () => {
    const doc = new jsPDF();
    const margin = 10;
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const lineHeight = 10;
    const maxLineWidth = pageWidth - margin * 2;
    let yPosition = margin + 10;

    doc.setFontSize(14);
    doc.setFont('Helvetica', 'bold');
    doc.text('ASSIGNMENT:', pageWidth / 2, margin, { align: 'center' });

    doc.setFontSize(12);
    doc.setFont('Helvetica', 'normal');

    const lines = doc.splitTextToSize(userInput, maxLineWidth);

    lines.forEach((line) => {
      if (yPosition + lineHeight > pageHeight - margin) {
        doc.addPage();
        yPosition = margin;
      }
      doc.text(line, margin, yPosition);
      yPosition += lineHeight;
    });

    doc.save('grammar-suggested-text.pdf');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-100">
       <header className="text-center mb-6">
        <h1 className="text-2xl font-bold text-blue-600 flex items-center justify-center">
          <FaPen className="mr-2" />
          Writing Assistant
        </h1>
        <p className="text-gray-600 mt-2">
          Enhance your writing with grammar and style suggestions.
        </p>
      </header>

      <textarea
        value={userInput}
        onChange={handleInputChange}
        placeholder="Enter your text here..."
        className="w-full max-w-lg h-40 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {/* Display suggestions directly below the textarea */}
      {suggestions.length > 0 && (
        <div className="mt-4 bg-white border border-gray-300 rounded-md shadow-lg p-4 w-full max-w-lg">
          <p className="font-semibold">Suggestions:</p>
          <ul className="list-disc pl-5">
            {suggestions}
          </ul>
        </div>
      )}

      {/* Download Button */}
      <button
        onClick={downloadPDF}
        className="mt-4 bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600"
      >
        Download PDF
      </button>
    </div>
  );
};

export default WritingAssistant;