import { IoSend } from "react-icons/io5";

interface Props {
  message: string;
  sendMessage: () => void;
  setMessage: (message: string) => void;
}
const SendMessage = ({ message, sendMessage, setMessage }: Props) => {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    sendMessage();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>);
    }
  };
  return (
    <div className="flex justify-between items-center px-4 py-3  border-t border-gray-600 bg-transparent min-h-[10vh]">
      <form className="flex-grow mx-4" onSubmit={handleSubmit}>
        <input
          className="w-full p-3 text-base placeholder-gray-500 bg-gray-200 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-700 focus:border-transparent resize-none"
          placeholder="Type your message here..."
          value={message}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setMessage(e.target.value)
          }
          onKeyDown={handleKeyDown}
        />
      </form>
      <button
        onClick={() => {
          sendMessage();
        }}
        className="p-3 bg-indigo-500 rounded-full text-white hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-150 ease-in-out"
      >
        <IoSend className="w-6 h-6" />
      </button>
    </div>
  );
};

export default SendMessage;
