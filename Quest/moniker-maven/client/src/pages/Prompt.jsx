import React, { useState } from 'react';

export default function Prompt() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:3001/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: message, model_name: "phi-3-gguf" })
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="p-8 bg-white dark:bg-darkTheme dark:text-white">
      <h1 className="text-4xl font-bold">Welcome to Moniker-Maven</h1>
      <p>This is a sample page content.</p>
      <form onSubmit={handleSubmit}>
        <div className="p-4">
          <label htmlFor="message">Message:</label>
          <textarea
            id="message"
            name="message"
            rows="4"
            required
            className="p-4 border border-gray-300 dark:border-gray-700 dark:text-black"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          ></textarea>
        </div>
        <button className="button block" type="submit">Submit</button>
      </form>
      {response && (
        <div className="mt-4 p-4 ">
          <h2 className="text-2xl font-bold">Response:</h2>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
