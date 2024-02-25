import React, { useState } from 'react';
import './UrlInput.css';

function UrlInput({ onSubmit }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [responseMessage, setResponseMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
		// console.log("URL to embedded :", url)
		const response = await fetch('http://localhost:5000/embed-and-store', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({ url }),
		  });
      if (response.ok) {
        const data = await response.json();
        setResponseMessage(data.message);
        onSubmit();
      } else {
        setResponseMessage('Error: Something went wrong.');
      }
    } catch (error) {
      console.error('Error:', error);
      setResponseMessage('Error: Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="urlinput">
      <div className="welcome-banner">
        <p>Welcome to my chatbot app</p>
      </div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter a URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Building Index...' : 'Submit'}
        </button>
      </form>
      {responseMessage && <p>{responseMessage}</p>}
    </div>
  );
}

export default UrlInput;