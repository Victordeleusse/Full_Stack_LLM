import React, { useState, useEffect } from 'react';
import UrlInput from './components/UrlInput';
import ChatInterface from './components/ChatInterface';

// App.js file will be the main “controller” for the application.
 
function App() {
  
  const [showChat, setShowChat] = useState(false); 
  const handleUrlSubmitted = () => {
    setShowChat(true);
  };
  // To delete the Pinecone index when the user leaves the page
  useEffect(() => {
    return () => {
      fetch('http://localhost:5000/delete-index', {
        method: 'POST',
      })
        .then((response) => {
          if (!response.ok) {
            console.error('Error deleting index:', response.statusText);
          }
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    };
  }, []);

  return (
    <div className="App">
      {!showChat ? (
        <UrlInput onSubmit={handleUrlSubmitted} />
      ) : (
        <ChatInterface />
      )}
    </div>
  );
}

export default App;
