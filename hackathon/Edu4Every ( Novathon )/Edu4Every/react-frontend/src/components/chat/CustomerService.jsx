import React, { useState, useEffect, useRef } from 'react';
import { collection, query, orderBy, onSnapshot, addDoc, where, doc, setDoc } from 'firebase/firestore';
import { auth, db } from '../../../firebase';
import { ScrollArea } from '../ui/ScrollArea';
import { Button } from '../ui/Button';

const CustomerService = () => {
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const q = query(
      collection(db, 'users'),
      orderBy('lastActive', 'desc')
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const chatsList = [];
      snapshot.forEach((doc) => {
        const userData = doc.data();
        chatsList.push({
          email: userData.email,
          chatId: userData.chatId,
          lastActive: userData.lastActive,
        });
      });
      setChats(chatsList);
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (selectedChat) {
      const q = query(
        collection(db, 'messages'),
        where('chatId', '==', selectedChat.chatId),
        orderBy('timestamp', 'asc')
      );

      const unsubscribe = onSnapshot(q, (snapshot) => {
        const messagesList = [];
        snapshot.forEach((doc) => {
          messagesList.push({ id: doc.id, ...doc.data() });
        });
        setMessages(messagesList);
      });

      return () => unsubscribe();
    }
  }, [selectedChat]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (newMessage.trim() && selectedChat) {
      const messageData = {
        text: newMessage,
        chatId: selectedChat.chatId,
        userEmail: auth.currentUser.email,
        userName: 'Customer Service',
        timestamp: new Date(),
        type: 'service'
      };

      // Add the new message to the state optimistically
    setMessages((prevMessages) => [
      ...prevMessages,
      { ...messageData, id: Date.now().toString() }, // Temporary ID
    ]);

    // Add to Firestore
    await addDoc(collection(db, 'messages'), messageData);

    // Update user's lastActive
    const userRef = doc(db, 'users', selectedChat.email);
    await setDoc(userRef, { lastActive: new Date() }, { merge: true });

    setNewMessage('');
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left sidebar */}
      <div className="w-1/3 bg-white shadow-lg flex flex-col min-w-[300px] max-w-[400px]">
        <div className="p-4 border-b">
          <h2 className="text-xl font-semibold">Active Chats</h2>
        </div>
        <ScrollArea className="flex-1" style={{ height: '550px'}}>
          <div className="py-2">
            {chats.map((chat) => (
              <div
                key={chat.chatId}
                onClick={() => setSelectedChat(chat)}
                className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                  selectedChat?.chatId === chat.chatId ? 'bg-blue-50' : ''
                }`}
              >
                <div className="font-medium">{chat.email}</div>
                <div className="text-xs text-gray-500">
                  Last active: {chat.lastActive.toDate().toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Right content area */}
      <div className="flex-1 flex flex-col bg-white ml-4 shadow-lg">
        {selectedChat ? (
          <>
            {/* Header */}
            <div className="p-4 border-b flex-none">
              <h3 className="font-medium">Chat with {selectedChat.email}</h3>
            </div>

            {/* Messages container */}
            <div className="flex-1 overflow-hidden relative">
              <ScrollArea className="absolute inset-0">
                <div className="p-4 space-y-4" style={{ height: '550px', marginTop:'3rem' }}>
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`${
                        message.type === 'service'
                          ? 'mr-auto bg-gray-100'
                          : 'ml-auto bg-blue-100'
                      } rounded-lg p-3 max-w-[80%]`}
                    >
                      <div className="text-sm text-gray-600 mb-1">
                        {message.userName}
                      </div>
                      {message.text}
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
            </div>

            {/* Input area */}
            <div className="flex-none p-4 border-t bg-white">
              <form onSubmit={sendMessage} className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="flex-1 p-2 border rounded-md"
                  placeholder="Type a message..."
                />
                <Button type="submit">Send</Button>
              </form>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            Select a chat to start messaging
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerService;