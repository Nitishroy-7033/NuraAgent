import React from 'react';

const ChatHeader = ({ agentName = "ChatAgent", onHistory, onClose, onNewChat }) => {
  return (
    <header className="chatkit-header">
      <div className="chatkit-header-info">
        <div className="chatkit-agent-avatar-mini">
          <span>A</span>
        </div>
        <h3>{agentName}</h3>
      </div>
      <div className="chatkit-header-actions">
        <button 
          className="chatkit-header-btn" 
          onClick={onNewChat}
          title="New Chat"
          aria-label="Start new chat"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        <button 
          className="chatkit-header-btn" 
          onClick={onHistory}
          title="Chat History"
          aria-label="View history"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="1 4 1 10 7 10"></polyline>
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
          </svg>
        </button>
        <button 
          className="chatkit-header-btn" 
          onClick={onClose}
          title="Close"
          aria-label="Close chat"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </header>
  );
};

export default ChatHeader;
