import { useState } from "react";

import FAQImage from "@/assets/images/FAQ.png";
const FAQ = () => {
  const FAQs = [
    {
      question: "1. What is DocuSolver?",
      answer:
        "DocuSolver is an innovative tool designed to help students streamline their exam preparation by automatically analyzing slides or PDF documents provided by teachers and generating answers to questions found within these materials. It enhances study efficiency by eliminating the need for manual searching.",
    },
    {
      question: "2. How does DocuSolver work?",
      answer:
        "DocuSolver works by scanning uploaded documents, such as slides and PDFs, using advanced algorithms to identify and extract potential exam questions. It then processes these to provide concise, accurate answers, helping students prepare for their exams more effectively.",
    },
    {
      question: "3. Is DocuSolver free to use?",
      answer: "DocuSolver is free to use.",
    },
    {
      question: "4. Which document formats are supported by DocuSolver?",
      answer:
        "DocuSolver currently supports PDF. We are continuously working to expand support to include more formats based on user feedback and demand.",
    },
    {
      question: "5. How can I get started with DocuSolver?",
      answer:
        "To get started with DocuSolver, upload your educational documents, and let our system analyze and generate answers to help you in your exam preparation.",
    },
  ];

  return (
    <div id="FAQ" className="my-10 mt-32">
      <h1 className="text-5xl tracking-wide font-bold text-black flex justify-center items-center my-16 mt-24">
        Frequently Asked Questions
      </h1>
      <div className="flex justify-evenly items-center w-full">
        <div className="w-7/12">
          <img src={FAQImage} alt="" />
        </div>
        <div className="text-base w-5/12">
          {FAQs.map(({ question, answer }) => {
            return (
              <FAQItem
                key={question + answer}
                question={question}
                answer={answer}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

interface FAQItem {
  question: string;
  answer: string;
}
const FAQItem = ({ question, answer }: FAQItem) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="rounded-lg mb-4">
      <button
        className={`w-full text-left py-2 px-4 shadow-lg rounded-lg text-base  text-black ${
          isOpen ? " " : "hover:bg-green-200"
        } focus:outline-none`}
        onClick={() => setIsOpen(!isOpen)}
      >
        {question}
        <span className="float-right">{isOpen ? "-" : "+"}</span>
        {isOpen && (
          <div className="p-4">
            <p className="text-gray-600">{answer}</p>
          </div>
        )}
      </button>
    </div>
  );
};

export default FAQ;
