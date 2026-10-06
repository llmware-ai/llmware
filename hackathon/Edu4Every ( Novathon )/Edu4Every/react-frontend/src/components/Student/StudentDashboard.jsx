import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Book,
  FileTextIcon, 
  VideoIcon, 
  MessageCircleIcon
} from 'lucide-react';

const StudentDashboard = () => {
  const navigate = useNavigate();
  const studentName = localStorage.getItem('studentName');

  const handleLogout = () => {
    localStorage.removeItem('userRole');
    localStorage.removeItem('studentName');
    localStorage.removeItem('teacherName');
    localStorage.removeItem('Id');
    navigate('/');
  };

  const dashboardItems = [
    {
      title: 'AI Learning',
      description: 'Schedule an AI-powered learning call, It will help student to learn more than what he learned manually and able to clear doubts.',
      link: '/call-feature',
      icon: VideoIcon,
      color: 'bg-purple-100 text-purple-600'
    },
    {
      title: 'Telegram Chat Bot',
      description: 'Our Telegram chat bot can do anything: text generation, audio processing, and image explanation',
      link: 'https://telegram.me/Edu4Every_bot',
      icon: MessageCircleIcon,
      color: 'bg-orange-100 text-orange-600'
    },
    {
      title: 'PDF Answer Finder',
      description: 'Find answers to your questions in PDFs',
      link: '/pdf-qa',
      icon: FileTextIcon,
      color: 'bg-blue-100 text-blue-600'
    },
    {
      title: 'Writing Assistant',
      description: 'Get suggestions for better grammar and clarity',
      link: '/writing-assistant',
      icon: Book,
      color: 'bg-green-100 text-green-600'
    }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-white shadow-xl rounded-xl overflow-hidden">
        {/* Navbar with student's name and logout button */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-white">Student Dashboard</h1>
          <div className="flex items-center space-x-4">
            {/* Display student's name */}
            {studentName && (
              <span className="text-white text-xl font-medium">
                Welcome, {studentName}!
              </span>
            )}
            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="bg-white text-blue-600 font-semibold px-4 py-2 rounded-lg shadow hover:bg-gray-100 transition-all"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Dashboard Items */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {dashboardItems.map((item, index) => {
              const Icon = item.icon;
              return (
                <div 
                  key={index} 
                  className="border rounded-lg shadow-md hover:shadow-xl transition-all duration-300"
                >
                  <div className="p-6 flex items-center space-x-4">
                    <div className={`${item.color} p-3 rounded-full`}>
                      <Icon className="w-8 h-8" />
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold text-gray-800">{item.title}</h2>
                      <p className="text-gray-600">{item.description}</p>
                    </div>
                  </div>
                  <div className="border-t p-4">
                    <Link 
                      to={item.link} 
                      className="w-full block text-center bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors"
                    >
                      Access
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
