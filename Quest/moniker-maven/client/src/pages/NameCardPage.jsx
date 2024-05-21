import React from 'react';
import renderNames from '../components/RenderNames'; 
import { Link } from 'react-router-dom'; 

import { useLocation } from 'react-router-dom';

const NameCardPage = () => {
  const location = useLocation();
  const response = JSON.parse(new URLSearchParams(location.search).get('response'));
  
  return (
    <div className='dark:bg-darkTheme'>

    <div className="max-w-md mx-auto p-6   bg-white rounded-lg shadow-md dark:bg-gray-700">
      <h1 className="text-2xl font-bold mb-4 text-center dark:text-white">🔍 Discover Enchanting Monikers 🔍</h1>

      <div className="space-y-4">
        {response && renderNames(response)}
      </div>

      <div className="flex justify-center mt-4">
        <Link to="/home" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Search New</Link>
      </div>
    </div>
    </div>
  );
};

export default NameCardPage;
