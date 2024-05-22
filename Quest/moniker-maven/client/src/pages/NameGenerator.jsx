import React, { useState } from 'react';
import '../components/spinner.css'; 
import renderNames from '../components/RenderNames'; 
import { useNavigate } from 'react-router-dom';

const NameGenerator = () => {
  const [formData, setFormData] = useState({
    nameType: 'baby',
    gender: 'unisex',
    petType: '',
    origin: '',
    length: 'medium',
    popularity: 'unique',
    initialLetter: '',
    easeOfPronunciation: 'easy',
    darkMode: false, // New state for dark mode
  });
  const navigate = useNavigate();
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse("");
    
    // Construct the query string from form data
    let query = `Generate a list of ${formData.nameType} names`;
    
    if (formData.nameType === 'pet' && formData.petType) {
      query += ` for a ${formData.petType}`;
    }
    
    query += ` that are ${formData.gender}, ${formData.length} in length, and ${formData.popularity}.`;
    
    if (formData.origin) {
      query += ` The names should have ${formData.origin} origin.`;
    }
    
    if (formData.initialLetter) {
      query += ` The names should start with "${formData.initialLetter}".`;
    }
    
    query += ` The names should be ${formData.easeOfPronunciation} to pronounce.`;
    query += ` Return the name in the form of word with meaning in bracket and then comma. format: word1(meaning1), word2(meaning2)`;
    
    console.log('Generated Query:', query);

    try {
      const res = await fetch("http://localhost:3001/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query, model_name: "phi-3-gguf" })
      });
      const data = await res.json();
      console.log('API Response:', data);
      setResponse(data.llm_response);
      // navigate('/name-cards'); // Redirect to name-cards page
      navigate(`/name-cards?response=${encodeURIComponent(JSON.stringify(data.llm_response))}`);

    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className={`  relative ${formData.darkMode ? 'dark:bg-darkTheme' : 'bg-white'}`}>
      {loading && (
        <div className="spinner-overlay">
          <div className="spinner"></div>
        </div>
      )}
      <div className={`max-w-md mx-auto p-6 rounded-lg shadow-md dark:bg-gray-400 ${loading ? 'blur' : ''} ${formData.darkMode ? 'dark:bg-darkTheme' : 'bg-white'}`}>
        <h1 className="text-2xl font-bold mb-4 text-center">Name Generator</h1>
        <form onSubmit={handleSubmit} className="space-y-4 ">
          {/* Form fields */}
          <div>
            <label className={`block text-sm font-medium ${formData.darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Name Type</label>
            <select name="nameType" value={formData.nameType} onChange={handleChange} className={`mt-1 block w-full p-2 border rounded-md ${formData.darkMode ? 'border-gray-700' : 'border-gray-300'}`}>
              <option value="baby">Baby</option>
              <option value="pet">Pet</option>
            </select>
          </div>
          
          {formData.nameType === 'pet' && (
            <div>
              <label className={`block text-sm font-medium ${formData.darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Pet Type</label>
              <input type="text" name="petType" value={formData.petType} onChange={handleChange} className={`mt-1 block w-full p-2 border rounded-md ${formData.darkMode ? 'border-gray-700' : 'border-gray-300'}`} placeholder="e.g., Dog, Cat" />
            </div>
          )}
          
          <div>
            <label className={`block text-sm font-medium ${formData.darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Gender</label>
            <select name="gender" value={formData.gender} onChange={handleChange} className={`mt-1 block w-full p-2 border rounded-md ${formData.darkMode ? 'border-gray-700' : 'border-gray-300'}`}>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="unisex">Unisex</option>
            </select>
          </div>
          
          <div>
            <label className={`block text-sm font-medium ${formData.darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Cultural Origin</label>
            <input type="text" name="origin" value={formData.origin} onChange={handleChange} className={`mt-1 block w-full p-2 border rounded-md ${formData.darkMode ? 'border-gray-700' : 'border-gray-300'}`} placeholder="e.g., English, French" />
          </div>
          
          <div>
            <label className={`block text-sm font-medium ${formData.darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Name Length</label>
            <select name="length" value={formData.length} onChange={handleChange} className={`mt-1 block w-full p-2 border rounded-md ${formData.darkMode ? 'border-gray-700' : 'border-gray-300'}`}>
              <option value="short">Short</option>
              <option value="medium">Medium</option>
              <option value="long">Long</option>
              </select>
          </div>
          
          <div>
            <label className={`block text-sm font-medium ${formData.darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Popularity</label>
            <select name="popularity" value={formData.popularity} onChange={handleChange} className={`mt-1 block w-full p-2 border rounded-md ${formData.darkMode ? 'border-gray-700' : 'border-gray-300'}`}>
              <option value="popular">Popular</option>
              <option value="uncommon">Uncommon</option>
              <option value="unique">Unique</option>
            </select>
          </div>
          
          <div>
            <label className={`block text-sm font-medium ${formData.darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Initial Letter</label>
            <input type="text" name="initialLetter" value={formData.initialLetter} onChange={handleChange} className={`mt-1 block w-full p-2 border rounded-md ${formData.darkMode ? 'border-gray-700' : 'border-gray-300'}`} placeholder="e.g., A, B" />
          </div>
          
          <div>
            <label className={`block text-sm font-medium ${formData.darkMode ? 'text-gray-300' : 'text-gray-700'}`}>Ease of Pronunciation</label>
            <select name="easeOfPronunciation" value={formData.easeOfPronunciation} onChange={handleChange} className={`mt-1 block w-full p-2 border rounded-md ${formData.darkMode ? 'border-gray-700' : 'border-gray-300'}`}>
              <option value="easy">Easy</option>
              <option value="moderate">Moderate</option>
              <option value="complex">Complex</option>
            </select>
          </div>
          
          <button type="submit" className={`w-full p-2 rounded-md ${formData.darkMode ? 'bg-gray-700 text-gray-300' : 'bg-blue-500 text-white'}`}>Generate Name</button>
        </form>
        
        {!loading && response && renderNames(response)}
      </div>
    </div>
  );
};

export default NameGenerator;

