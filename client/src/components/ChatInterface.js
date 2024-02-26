import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import io from 'socket.io-client';
import '../styles/ChatInterface.css';

const socket = io('http://localhost:5000');

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    socket.on('new_message', (message) => {
      console.log("Response from the BACK received listening on new_message")
      setMessages(messages => [...messages, message]);
    });

    // Cleanup on component unmount
    return () => {
      socket.off('new_message');
    };
  }, []);

  const handleSendMessage = (event) => {
    event.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = { text: inputText, isBot: false };
    setMessages(messages => [...messages, userMessage]);
  
    const chatHistory = messages.map(message => ({ text: message.text, isBot: message.isBot }));
    chatHistory.push(userMessage);
  
    socket.emit('send_question', {
      question: inputText,
      chatHistory: chatHistory,
    });

    setInputText('');
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <div className="centered-header">Chat with Bot</div>
      </header>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input" onSubmit={handleSendMessage}>
        <input
          type="text"
          placeholder="Please, send your question"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          required
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default ChatInterface;
