import React, { useState } from 'react';
import axios from 'axios';

const ChatBox = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

    const sendMessage = async () => {
        const response = await axios.post('/api/chat', { query: input });
        setMessages([...messages, { user: input, bot: response.data.response }]);
        setInput('');
    };

    return (
        <div>
            <div className="chatbox">
                {messages.map((msg, index) => (
                    <div key={index}>
                        <p><strong>You:</strong> {msg.user}</p>
                        <p><strong>Bot:</strong> {msg.bot}</p>
                    </div>
                ))}
            </div>
            <input 
                type="text" 
                value={input} 
                onChange={(e) => setInput(e.target.value)} 
                placeholder="Type a message" 
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
};

export default ChatBox;
