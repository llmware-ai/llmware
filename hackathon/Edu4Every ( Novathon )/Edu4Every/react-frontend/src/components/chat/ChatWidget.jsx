import React, { useState, useEffect, useRef } from 'react';
import { collection, addDoc, query, orderBy, onSnapshot, where, serverTimestamp } from 'firebase/firestore';
import { X, Send } from 'lucide-react';
import { ScrollArea } from '../ui/ScrollArea';
import { Button } from '../ui/Button';
import { db } from '../../../firebase';
import { getGreeting } from './authUtils';

const ChatWidget = ({ userEmail, userName, autoOpen = false }) => {
  const [isOpen, setIsOpen] = useState(autoOpen);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  useEffect(() => {
    const chatId = `chat_${userEmail.toLowerCase()}`;
    let unsubscribe;

    try {
      const q = query(
        collection(db, 'messages'),
        where('chatId', '==', chatId),
        orderBy('timestamp', 'asc')
      );

      unsubscribe = onSnapshot(q, (snapshot) => {
        const messagesList = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data(),
          timestamp: doc.data().timestamp?.toDate() || new Date()
        }));
        setMessages(messagesList);
      }, (error) => {
        console.error("Error fetching messages:", error);
      });
    } catch (error) {
      console.error("Error setting up messages listener:", error);
    }

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, [userEmail]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (newMessage.trim() && !isLoading) {
      setIsLoading(true);
      try {
        const chatId = `chat_${userEmail.toLowerCase()}`;
        const messageData = {
          text: newMessage.trim(),
          chatId,
          userEmail,
          userName: userName || userEmail,
          timestamp: serverTimestamp(),
          type: 'user'
        };
        
        const optimisticMessage = {
          ...messageData,
          id: Date.now().toString(),
          timestamp: new Date()
        };
        setMessages(prev => [...prev, optimisticMessage]);
        setNewMessage('');
        
        await addDoc(collection(db, 'messages'), messageData);
      } catch (error) {
        console.error("Error sending message:", error);
        setMessages(prev => prev.filter(msg => msg.id !== Date.now().toString()));
        setNewMessage(newMessage);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = timestamp instanceof Date ? timestamp : timestamp.toDate();
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      {isOpen && (
        <div className="fixed bottom-20 right-8 w-80 bg-white rounded-lg shadow-xl flex flex-col" style={{ height: '500px' }}>
          {/* Header */}
          <div className="flex-none flex justify-between items-center p-4 bg-blue-600 text-white rounded-t-lg">
            <div>
              <h3 className="font-semibold">Chat with us</h3>
              <p className="text-sm">
                Welcome {userName || userEmail}, {getGreeting()}
              </p>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="hover:bg-blue-700 p-1 rounded transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 min-h-0"> {/* min-h-0 is crucial for flex child scrolling */}
            <ScrollArea 
              ref={scrollAreaRef}
              className="h-full"
            >
              <div className="p-4 space-y-4 overflow-y-auto" style={{ height: '330px' }}>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex flex-col ${
                      message.type === 'user' ? 'items-end' : 'items-start'
                    }`}
                  >
                    <div
                      className={`${
                        message.type === 'user'
                          ? 'bg-blue-100 text-blue-900'
                          : 'bg-gray-100 text-gray-900'
                      } rounded-lg p-3 max-w-[80%] break-words`}
                    >
                      <div className="text-xs text-gray-600 mb-1">
                        {message.userName} • {formatTimestamp(message.timestamp)}
                      </div>
                      <div className="text-sm">{message.text}</div>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
          </div>

          {/* Input Form */}
          <div className="flex-none p-4 bg-white border-t">
            <form 
              onSubmit={sendMessage} 
              className="flex gap-2"
            >
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                className="flex-1 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Type a message..."
                disabled={isLoading}
              />
              <Button 
                type="submit"
                disabled={isLoading}
                className={`${isLoading ? 'opacity-50' : ''} px-3`}
              >
                <Send className="w-4 h-4" />
              </Button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWidget;