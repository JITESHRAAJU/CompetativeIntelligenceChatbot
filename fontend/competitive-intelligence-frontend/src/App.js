// File: src/App.jsx
import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import UserInputArea from './components/UserInputArea';
import CompanyInfoPanel from './components/CompanyInfoPanel';

function App() {
  const [messages, setMessages] = useState([
    {
      type: 'system',
      content: 'Welcome to the Competitive Intelligence Assistant! How can I help you track your competitors today?'
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [industry, setIndustry] = useState('');
  const [competitors, setCompetitors] = useState([]);
  const [userId] = useState(`user_${Math.random().toString(36).substring(2, 9)}`);
  
  // Function to handle sending messages
  const sendMessage = async (message) => {
    if (!message.trim()) return;
    
    // Add user message to chat
    setMessages(prev => [...prev, { type: 'user', content: message }]);
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          message: message,
          industry: industry || null,
          competitors: competitors.length > 0 ? competitors : null
        }),
      });
      
      const data = await response.json();
      
      // Add assistant response to chat
      setMessages(prev => [...prev, { type: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: 'Sorry, there was an error communicating with the agent. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };
  
  // Handle industry update
  const updateIndustry = (newIndustry) => {
    setIndustry(newIndustry);
  };
  
  // Handle competitors update
  const updateCompetitors = (newCompetitors) => {
    setCompetitors(newCompetitors);
  };
  
  return (
    <div className="app">
      <Header />
      <div className="main-container">
        <CompanyInfoPanel 
          industry={industry} 
          competitors={competitors} 
          updateIndustry={updateIndustry}
          updateCompetitors={updateCompetitors}
        />
        <div className="chat-container">
          <ChatWindow messages={messages} loading={loading} />
          <UserInputArea sendMessage={sendMessage} loading={loading} />
        </div>
      </div>
    </div>
  );
}

export default App;