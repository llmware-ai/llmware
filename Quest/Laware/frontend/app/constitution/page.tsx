"use client";

import React, { useState } from "react";
import './style.module.css';
import axios from "axios";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from "@chatscope/chat-ui-kit-react";

const systemMessage = {
  role: "system",
  content:
    "Explain things like you're talking to a software professional with 2 years of experience.",
};

interface MessageType {
  message: string;
  sentTime?: string;
  sender: string;
  direction?: "incoming" | "outgoing";
}

const constitution: React.FC = () => {
  const [messages, setMessages] = useState<MessageType[]>([
    {
      message: "Ask anything related to Constitution of Nepal 2015 A.D.",
      sentTime: "just now",
      sender: "ChatGPT",
    },
  ]);

  const [isTyping, setIsTyping] = useState<boolean>(false);

  const handleSend = async (message: string) => {
    const newMessage: MessageType = {
      message,
      direction: "outgoing",
      sender: "user",
    };

    const newMessages = [...messages, newMessage];
    setMessages(newMessages);

    setIsTyping(true);
    await processMessageToChatGPT(newMessages);
  };

  const processMessageToChatGPT = async (chatMessages: MessageType[]) => {
    const apiMessages = chatMessages.map((messageObject) => {
      let role = messageObject.sender === "ChatGPT" ? "assistant" : "user";
      return { role: role, content: messageObject.message };
    });

    const apiRequestBody = {
      // model: "gpt-3.5-turbo",
      messages: [systemMessage, ...apiMessages],
    };

    // console.log(apiRequestBody.messages[apiRequestBody.messages.length - 1].content)
    let query_text =
      apiRequestBody.messages[apiRequestBody.messages.length - 1].content;

    try {
      const response = await axios.post("http://127.0.0.1:8000/answer", {
        query: query_text,
      });
      setMessages([
        ...chatMessages,
        {
          message: response.data.answer,
          sender: "ChatGPT",
        },
      ]);
    } catch (error) {
      console.error("There was an error making the request!", error);
      setMessages([
        ...chatMessages,
        {
          message: "Error retrieving answer. Please try again.",
          sender: "ChatGPT",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="constitution">
      <div style={{ position: "relative", height: "500px", width: "750px" }}>
        <MainContainer>
          <ChatContainer>
            <MessageList
              scrollBehavior="smooth"
              typingIndicator={
                isTyping ? (
                  <TypingIndicator content="Getting Result using LLMware" />
                ) : null
              }
            >
              {messages.map((message, i) => (
                <Message key={i} model={message} />
              ))}
            </MessageList>
            <MessageInput placeholder="Type message here" onSend={handleSend} />
          </ChatContainer>
        </MainContainer>
      </div>
    </div>
  );
};

export default constitution;
