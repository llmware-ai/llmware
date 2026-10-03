import React, { useState, useRef, useEffect } from "react";
import "./Chatui.scss";
import { motion } from "motion/react";
import { baseUrl } from "../../constants";
import { useStore } from "../../context/StoreContext";

import { ThreeDots } from "react-loader-spinner";

const ChatComponent = ({ chatPopup, setChatPopup, uid }) => {
  const { wallet, setWallet } = useStore();
  const [messages, setMessages] = useState([
    { id: 1, text: "Welcome! How can I help you today?", sender: "bot" },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const messagesEndRef = useRef(null);

  const [chatLoad, setChatLoad] = useState(false);

  // Function to handle sending the message
  const handleSendMessage = async () => {
    if (inputMessage.trim() === "") return;

    // Add user message to chat
    const newUserMessage = {
      id: messages.length + 1,
      text: inputMessage,
      sender: "user",
    };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setChatLoad(true);
    try {
      // Call the external API with the user's input
      const response = await fetch(`${baseUrl}/chat/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Address: wallet,
        },
        body: JSON.stringify({ prfid: uid, prompt: inputMessage, history: [] }),
      });

      // Handle the API response
      if (!response.ok) {
        throw new Error("Failed to fetch chat response");
      }

      const data = await response.json();

      // Add bot response to chat
      const newBotMessage = {
        id: messages.length + 2,
        text: data.res,
        sender: "bot",
      };
      setMessages((prevMessages) => [...prevMessages, newBotMessage]);
      setChatLoad(false);
    } catch (error) {
      setChatLoad(false);
      console.error("Error:", error);
      const errorMessage = {
        id: messages.length + 2,
        text: "Sorry, there was an error processing your request.",
        sender: "bot",
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    }

    setInputMessage("");
  };

  // Scroll to the latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-page">
      <div className="close-btn" onClick={() => setChatPopup(!chatPopup)}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width={67}
          height={67}
          fill="none"
        >
          <rect width={66} height={66} x={0.5} y={0.5} fill="#fff" rx={33} />
          <rect
            width={66}
            height={66}
            x={0.5}
            y={0.5}
            stroke="#E3E3E5"
            rx={33}
          />
          <path
            fill="#4F4F4F"
            d="m34 31.5 8-8 2 1.833-8.167 8.167L44 41.667 41.667 44 33.5 35.833 25.333 44 23 41.667l8.167-8.167L23 25.333 25.333 23z"
          />
        </svg>
      </div>
      <motion.div
        className="chat-container"
        initial={{ scale: 0.4 }}
        animate={{ scale: 1 }}
        transition={{
          duration: 0.2,
        }}
      >
        <div className="messages-container">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.sender}`}>
              <div className="message-content">{message.text}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
          {chatLoad && (
            <div className="chat-load">
              <ThreeDots
                visible={true}
                height="30"
                width="30"
                color="#000"
                radius="9"
                ariaLabel="three-dots-loading"
                wrapperStyle={{}}
                wrapperClass=""
              />
            </div>
          )}
        </div>

        <div className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder="Type a message..."
            className="message-input"
          />
          <button onClick={handleSendMessage} className="send-button">
            Send
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default ChatComponent;
