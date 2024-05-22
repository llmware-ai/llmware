import Messages from "@/components/Messages";
import SendMessage from "@/components/SendMessage";
import Layout from "@/layout/Layout";
import { Message } from "@/types/Message";
import axios from "axios";
import { useState, useRef, useEffect } from "react";



const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [message, setMessage] = useState<string>(" ");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addMessage = (text: string, sender: string) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { text, sender, username: sender },
    ]);
  };

  const sendMessage = async () => {
    const userMessage: Message = {
      text: message,
      sender: "User",
      username: "User",
    };

    const loadingMessage: Message = {
      text: "DocuAI is thinking",
      sender: "DocuAI",
      username: "DocuAI",
      isLoading: true,
    };

    setMessages((currentMessages: Message[]) => [
      ...currentMessages,
      userMessage,
      loadingMessage,
    ]);

    setMessage("");

    console.log(message)
    try {
      // API Call to /ask endpoint
      const response = await axios.post('http://127.0.0.1:8000/api/ask', {
        question: message,
      });

      console.log(response)
      const aiResponse = response.data.answer

      const aiMessage: Message = {
        text: aiResponse,
        sender: "DocuAI",
        username: "DocuAI",
      };

      setMessages((currentMessages: Message[]) => {
        return currentMessages.map((m, index) =>
          index === currentMessages.length - 1 ? aiMessage : m
        );
      });

    } catch (error) {
      console.error("Error sending message:", error);
      addMessage("Error occurred while fetching AI response", "DocuAI");
    }
  };

  return (
    <>
      <Layout className="px-64 flex justify-center items-center bg-gray-100">
        <div className="w-[50vw] max-w-[70vw] flex flex-col ">
          <div className="flex-grow flex flex-col overflow-y-auto">
            <Messages messages={messages} />
            <div ref={messagesEndRef} />
          </div>
          <SendMessage
            message={message}
            setMessage={setMessage}
            sendMessage={sendMessage}
          />
        </div>
      </Layout>
    </>
  );
};

export default ChatPage;
