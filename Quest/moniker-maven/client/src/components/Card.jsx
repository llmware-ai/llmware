import React from 'react';

const NameCard = ({ word, meaning }) => {
  return (
    <div className="bg-gradient-to-r from-purple-400 via-pink-500 to-red-500 p-2 rounded-lg transition-transform transform hover:scale-105 duration-300">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-lg hover:shadow-2xl flex flex-col">
        <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 bg-clip-text text-transparent bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 mb-2">
          {word}
        </h3>
        {meaning && (
          <div className="flex items-center">
            <i className="far fa-heart text-red-500 mr-1"></i>
            <p className="text-gray-600 dark:text-gray-300">{meaning}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NameCard;
