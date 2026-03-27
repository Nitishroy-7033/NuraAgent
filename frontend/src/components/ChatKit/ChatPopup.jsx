import React, { useState } from 'react';
import ChatHeader from './ChatHeader';
import ChatBody from './ChatBody';
import ChatFooter from './ChatFooter';
import ChatHistory from './ChatHistory';

const ChatPopup = ({ 
  isOpen, 
  agentName, 
  messages, 
  suggestions, 
  onSuggestionClick, 
  onSendMessage, 
  onNewChat,
  loading, 
  messageContainerRef,
  toggleChat
}) => {
  const [showHistory, setShowHistory] = useState(false);

  // Sample history data
  const sampleHistory = [
    { title: "Project Brainstorming", date: "2 hours ago" },
    { title: "React Component Help", date: "Yesterday" },
    { title: "API Integration Guide", date: "Mar 24" }
  ];

  const toggleHistory = () => setShowHistory(!showHistory);

  return (
    <div className={`chatkit-popup ${isOpen ? 'open' : ''}`}>
      <div className="chatkit-main-container">
        <div className="chatkit-content-area">
          <ChatHeader 
            agentName={agentName} 
            onHistory={toggleHistory} 
            onClose={toggleChat} 
            onNewChat={onNewChat}
          />
          <ChatBody 
            messages={messages} 
            agentName={agentName} 
            suggestions={suggestions}
            onSuggestionClick={onSuggestionClick}
            messageContainerRef={messageContainerRef}
          />
          <ChatFooter 
            onSendMessage={onSendMessage} 
            loading={loading} 
          />
        </div>

        <ChatHistory 
          isOpen={showHistory} 
          onClose={toggleHistory}
          history={sampleHistory}
          onHistorySelect={(item) => {
            console.log("Selected history item:", item);
            toggleHistory();
          }}
        />
      </div>
    </div>
  );
};

export default ChatPopup;
