import React, { useEffect, useRef } from 'react';
import ChatBubble from './ChatBubble';

const ChatField = ({ message }) => {
    const chatBottomRef = useRef(null);
    console.log(message)

    useEffect(() => {
        chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }, [message]);

    return (
        <div className="px-4 space-y-4">
            {/* Loop through the messages array and render a ChatBubble for each message */}
            {message.map((message) => (
                <ChatBubble key={message.id} message={message} />
            ))}
            {/* Scroll target to make sure the view is scrolled to the latest message */}
            <div ref={chatBottomRef} />
        </div>
    );
};

export default ChatField;
