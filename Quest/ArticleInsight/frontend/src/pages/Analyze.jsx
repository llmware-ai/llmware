import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import axios from 'axios';

const SentimentMessage = ({ sentiment }) => {
  let message = '';

  switch (sentiment) {
    case 'positive':
      message = 'The average response in comments reflects positivity 😊';
      break;
    case 'negative':
      message = 'The average response in comments reflects negativity 😞';
      break;
    case 'neutral':
      message = 'The average response in comments is neutral 😐';
      break;
    case '':
    case undefined:
    case null:
      message = 'The comment section is empty 🗨️';
      break;
    default:
      message = `The average comment response is '${sentiment}'`;
  }

  return <p className="mt-6 text-xl text-gray-500">{message}</p>;
};

const Analyze = () => {
  const [articleData, setArticleData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [question, setQuestion] = useState('');
  const [answerData, setAnswerData] = useState({ answer: '', explanation: '' });
  const [questionsans, setQuestionsans] = useState([]);
  const [questionLoading, setQuestionLoading] = useState(false);
  const [questionError, setQuestionError] = useState('');

  useEffect(() => {
    const fetchArticleData = () => {
      const storedData = localStorage.getItem('articleData');
      if (storedData) {
        const parsedData = JSON.parse(storedData);
        // console.log('Retrieved articleData from second page:', parsedData); // Debugging line
        setArticleData(parsedData);
        setIsLoading(false);
      } else {
        setError('No article data found. Please go back and submit an article URL.');
        setIsLoading(false);
      }
    };

    fetchArticleData();
  }, []);

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();

    if (!articleData || !articleData.url) {
      setError('Article URL is missing. Please go back and submit an article URL.');
      return;
    }

    try {
      setQuestionLoading(true);
      setQuestionError('');

      const formData = new FormData();
      formData.append('url', articleData.url);
      formData.append('question', question);

      const response = await axios.post('http://localhost:8000/get_answer/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data', // Send form data
        },
      });
      const { answer, explanation } = response.data.answer;

      setQuestionsans([[question, answer, explanation], ...questionsans]);
      setAnswerData({
        answer,
        explanation,
      });
      setQuestion(''); // Clear the input field after submission
    } catch (err) {
      setQuestionError('Error processing the question. Please try again.');
      console.error('Error:', err);
    } finally {
      setQuestionLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-white">
        <div className="bg-black text-white">
          <Navbar />
        </div>
        <div className="flex-1 flex justify-center items-center bg-white">
          <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-gray-900"></div>
        </div>
        <Footer />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col bg-white">
        <div className="bg-black text-white">
          <Navbar />
        </div>
        <div className="flex-1 flex justify-center items-center bg-white">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-white">
      <div className="bg-black text-white">
        <Navbar />
      </div>
      <AnalyzeComponent
        articleData={articleData}
        answerData={answerData}
        handleQuestionSubmit={handleQuestionSubmit}
        setQuestion={setQuestion}
        question={question}
        questionsans={questionsans}
        questionLoading={questionLoading}
        questionError={questionError}
      />
      <Footer />
    </div>
  );
};

export default Analyze;

const AnalyzeComponent = ({
  articleData,
  answerData,
  handleQuestionSubmit,
  setQuestion,
  question,
  questionsans,
  questionLoading,
  questionError,
}) => {
  // Ensure tags are unique and limit to 6 tags, ignoring case
  const uniqueTags = articleData?.tags?.tags
    ? Array.from(new Set(JSON.parse(articleData.tags.tags).map((tag) => tag.toLowerCase()))).slice(0, 6)
    : [];

  return (
    <div className="container mx-auto my-12 px-4 md:px-6 lg:px-8">
      <article className="prose">
        <h1 className="text-5xl font-bold tracking-tight text-black capitalize">
          {articleData?.topic?.topics?.[0]}
        </h1>
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {uniqueTags.length > 0 &&
            uniqueTags.map((tag, index) => (
              <span key={index} className="rounded-md bg-gray-100 px-3 py-1 text-lg font-medium">
                {tag}
              </span>
            ))}
        </div>
        <hr className="my-6 border-gray-300" />
        <h2 className="text-4xl font-bold tracking-tight text-black mt-10">Summary</h2>
        <ul className="mt-6 text-xl text-gray-500 list-disc list-inside">
          {articleData?.summary?.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
        <hr className="my-6 border-gray-300" />
        <h2 className="text-4xl font-bold tracking-tight text-black mt-10">Comment Sentiment Analysis</h2>
        <SentimentMessage sentiment={articleData?.sentiment?.sentiment?.[0]} />
      </article>
      <hr className="my-6 border-gray-300" />
      <section className="mt-12">
        <h2 className="text-3xl font-bold text-black">Ask a Question to AI</h2>
        <form className="mt-4 space-y-4" onSubmit={handleQuestionSubmit}>
          <div>
            <label className="block text-lg font-medium text-gray-700" htmlFor="question">
              Your Question Related To Article
            </label>
            <textarea
              className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-lg text-gray-900 shadow-sm focus:border-gray-500 focus:outline-none focus:ring-gray-500 resize-none"
              id="question"
              placeholder="Enter your question here..."
              rows={3}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          </div>
          <div className="flex justify-end">
            <button
              className="inline-flex items-center rounded-md bg-gray-900 px-4 py-2 text-lg font-medium text-white shadow-sm transition-colors hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-500"
              type="submit"
              disabled={questionLoading}
            >
              {questionLoading ? (
                <svg
                  className="animate-spin h-5 w-5 text-white mr-3"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zM2 12a10 10 0 0110-10V0C4.477 0 0 4.477 0 10h2z"
                  ></path>
                </svg>
              ) : (
                'Ask AI'
              )}
            </button>
          </div>
          {questionError && <p className="text-red-500 text-sm mt-2">{questionError}</p>}
        </form>
      </section>
      <hr className="my-6 border-gray-300" />
      <section className="mt-12">
        <h2 className="text-3xl font-bold text-black">AI Responses</h2>
        {questionsans.map((qa, index) => (
          <div key={index} className="mt-4 rounded-md border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-lg text-gray-700">
              <strong>Question:</strong> {qa[0]}
            </p>
            <p className="text-lg text-gray-700">
              <strong>Answer:</strong> {qa[1]}
            </p>
            <p className="text-lg text-gray-500 mt-2">
              <strong>Explanation:</strong> {qa[2]}
            </p>
            <div className="mt-4 flex items-center space-x-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-500">
                <svg
                  className="h-5 w-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    clipRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z"
                    fillRule="evenodd"
                  />
                </svg>
              </div>
              <span className="text-lg font-medium text-gray-500">AI Assistant</span>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
};
