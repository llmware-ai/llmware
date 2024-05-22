import React from 'react';

const ContactUs = () => {
  return (
    <div className="bg-gray-100 dark:bg-darkTheme dark:text-white py-16">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl md:text-5xl font-bold text-center mb-8">Get in Touch</h2>
        <p className="text-lg md:text-xl text-center max-w-2xl mx-auto mb-12">
          We'd love to hear from you! Reach out with any questions or feedback.
        </p>
        <form className="max-w-xl mx-auto bg-white p-8 shadow-md rounded-lg">
          <div className="mb-6">
            <label htmlFor="name" className="block text-gray-700 font-bold mb-2">
              Your Name
            </label>
            <input
              id="name"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              type="text"
              placeholder="Your Name"
            />
          </div>
          <div className="mb-6">
            <label htmlFor="email" className="block text-gray-700 font-bold mb-2">
              Your Email
            </label>
            <input
              id="email"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              type="email"
              placeholder="Your Email"
            />
          </div>
          <div className="mb-6">
            <label htmlFor="message" className="block text-gray-700 font-bold mb-2">
              Your Message
            </label>
            <textarea
              id="message"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              rows="4"
              placeholder="Your Message"
            ></textarea>
          </div>
          <button
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
            type="submit"
          >
            Send Message
          </button>
        </form>
      </div>
    </div>
  );
};

export default ContactUs;
