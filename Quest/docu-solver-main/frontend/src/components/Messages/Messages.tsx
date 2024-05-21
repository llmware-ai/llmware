import { Message } from "@/types/Message";
import React from "react";
import { FaUser, FaRobot } from "react-icons/fa";

interface Props {
  messages: Message[];
}

const Messages: React.FC<Props> = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] min-h-[90vh]">
        <p className="text-lg text-gray-500">No new messages</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full px-4 py-5 h-[60vh] min-h-[85vh] bg-stone-300 my-5 rounded-xl ">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${
            message.username === "User" ? "justify-end" : "justify-start"
          } items-end gap-2`}
        >
          {message.username !== "User" && (
            <div className="flex items-end">
              <FaRobot className="text-3xl text-green-500 mr-2" />
              <div className="max-w-lg break-words p-3 rounded-lg shadow-lg bg-gray-700 text-white">
                <p>{message.text}</p>
              </div>
            </div>
          )}
          {message.username === "User" && (
            <div className="flex items-end">
              <div className="max-w-lg break-words p-3 rounded-lg shadow-md bg-indigo-800 text-white">
                <p>{message.text}</p>
              </div>
              <FaUser className="text-3xl text-stone-400 ml-2" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default Messages;
