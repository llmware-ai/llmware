import React, { useState } from 'react';
import axios from 'axios';
import jsPDF from 'jspdf';

const ResumeBuilderPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    education: 'high_school',
    degree: '',
    skills: '',
    experience: '',
    projects: '',
    job_title: ''
  });

  const [generatedResume, setGeneratedResume] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await axios.post(
        'https://a1e5-111-92-80-102.ngrok-free.app/process_carrier_guidance/process-guidance',
        JSON.stringify(formData),
        {
          headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json'
          }
        }
      );
      setGeneratedResume(response.data.advice);
    } catch (error) {
      console.error('Resume generation error:', error);
      setError('Error generating resume. Please try again later.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const downloadPDF = () => {
    if (!generatedResume) return;

    const doc = new jsPDF();
    doc.setFontSize(12);
    doc.text("Generated Resume", 10, 10);
    const lines = generatedResume.split('\n');
    lines.forEach((line, index) => {
      doc.text(line, 10, 20 + (index * 10));
    });

    doc.save('generated_resume.pdf');
  };

  return (
    <div className="container mx-auto px-6 py-12 flex flex-col md:flex-row items-center justify-between bg-gradient-to-r from-blue-500 to-purple-500">
      <div className="bg-white shadow-2xl rounded-lg p-8 w-full md:w-1/2 lg:w-1/3 mx-auto">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">Resume Builder</h1>

        {error && (
          <div className="bg-red-100 text-red-800 p-4 rounded-lg mb-4">
            <strong>Error:</strong> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="flex flex-col">
            <label className="text-lg font-medium text-gray-700">Full Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your full name"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="flex flex-col">
              <label className="text-lg font-medium text-gray-700">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your email"
                required
              />
            </div>
            <div className="flex flex-col">
              <label className="text-lg font-medium text-gray-700">Phone Number</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                className="p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your phone number"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="flex flex-col">
              <label className="text-lg font-medium text-gray-700">Education Level</label>
              <select
                name="education"
                value={formData.education}
                onChange={handleInputChange}
                className="p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="high_school">High School</option>
                <option value="bachelors">Bachelor's Degree</option>
                <option value="masters">Master's Degree</option>
              </select>
            </div>
            <div className="flex flex-col">
              <label className="text-lg font-medium text-gray-700">Degree/Major</label>
              <input
                type="text"
                name="degree"
                value={formData.degree}
                onChange={handleInputChange}
                className="p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Computer Science"
              />
            </div>
          </div>

          {['skills', 'experience', 'projects', 'job_title'].map((field, index) => (
            <div key={index} className="flex flex-col">
              <label className="text-lg font-medium text-gray-700">{field.replace(/_/g, ' ').toUpperCase()}</label>
              <textarea
                name={field}
                value={formData[field]}
                onChange={handleInputChange}
                rows={3}
                className="p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={`Describe your ${field.replace(/_/g, ' ')}`}
              ></textarea>
            </div>
          ))}

          <button
            type="submit"
            className={`w-full py-3 rounded-lg text-white font-semibold ${isSubmitting ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'}`}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Generating...' : 'Generate Resume'}
          </button>
        </form>
      </div>

      {generatedResume && (
        <div className="bg-white shadow-2xl rounded-lg p-8 w-full md:w-1/2 lg:w-1/3 mt-12 md:mt-0 mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Generated Resume</h2>
          <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">{generatedResume}</pre>
          <button
            onClick={downloadPDF}
            className="mt-6 w-full py-3 rounded-lg bg-green-500 text-white font-semibold hover:bg-green-600"
          >
            Download Resume as PDF
          </button>
        </div>
      )}
    </div>
  );
};

export default ResumeBuilderPage;
