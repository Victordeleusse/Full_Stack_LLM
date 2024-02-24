import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import io from 'socket.io-client';

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

// function ChatInterface() {
//   const [messages, setMessages] = useState([]);
//   const [inputText, setInputText] = useState('');
//   const messagesEndRef = useRef(null);

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   };

//   useEffect(scrollToBottom, [messages]);

//   const handleSendMessage = async (event) => {
//     event.preventDefault();
  
//     if (!inputText.trim()) return;
  
//     const userMessage = { text: inputText, isBot: false };
//     setMessages(messages => [...messages, userMessage]);
  
//     const chatHistory = messages.map(message => ({ text: message.text, isBot: message.isBot }));
//     chatHistory.push(userMessage);
  
//     const requestBody = {
//       question: inputText,
//       chatHistory: chatHistory,
//     };
  
//     try {
//         console.log("Request from FRONT :", requestBody.question)
//         const response = await fetch('http://localhost:5000/handle-query', {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify(requestBody),
//         });
//         const data = await response.json();
//         if (data.answer) {
//           const botMessage = { text: data.answer, isBot: true };
//           setMessages(messages => [...messages, botMessage]);
//         } else {
//           console.error("No answer received from the backend.");}
//     } 
//     catch (error) {
//       console.error("Failed to fetch:", error);
//     }

//     setInputText(''); 
// };
  //   setInputText('');
  
  //   if (response.ok && response.body) {
  //     const reader = response.body.getReader();
  //     reader.read().then(function processText({ done, value }) {
  //       if (done) {
  //         console.log("Stream complete");
  //         return;
  //       }
  
  //       const decoder = new TextDecoder();
  //       const text = decoder.decode(value);
  //       const data = JSON.parse(text);
  
  //       const botMessage = { text: data.answer, isBot: true };
  //       setMessages(messages => [...messages, botMessage]);
  
  //       return reader.read().then(processText);
  //     });
  //   } else {
  //     console.error("Failed to fetch");
  //   }
  // };

  return (
    <div className="chat-container">
      <header className="chat-header">Chat with Bot</header>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input" onSubmit={handleSendMessage}>
        <input
          type="text"
          placeholder="Type a question and press enter ..."
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
