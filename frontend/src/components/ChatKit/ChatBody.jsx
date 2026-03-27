import React from 'react';

const ChatBody = ({ 
  messages = [], 
  agentName = "ChatAgent", 
  suggestions = [], 
  onSuggestionClick,
  messageContainerRef
}) => {
  const hasMessages = messages.length > 0;

  return (
    <div className="chatkit-body" ref={messageContainerRef}>
      {!hasMessages ? (
        <div className="chatkit-empty-state">
          <div className="chatkit-agent-avatar">
            <span>A</span>
          </div>
          <h1>{agentName}</h1>
          <p>How can I help you today?</p>
          
          {suggestions.length > 0 && (
            <div className="chatkit-suggestions">
              {suggestions.map((s, idx) => (
                <button 
                  key={idx} 
                  className="chatkit-suggestion-btn" 
                  onClick={() => onSuggestionClick(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="chatkit-messages">
          {messages.map((msg, idx) => (
            <div 
              key={idx} 
              className={`chatkit-message ${msg.role === 'user' ? 'user' : 'agent'}`}
              style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                background: msg.role === 'user' ? 'var(--chatkit-primary)' : 'var(--chatkit-border)',
                color: msg.role === 'user' ? 'white' : 'var(--chatkit-text)',
                padding: '10px 16px',
                borderRadius: '16px',
                borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                borderBottomLeftRadius: msg.role === 'agent' ? '4px' : '16px',
                maxWidth: '85%',
                fontSize: '14px',
                lineHeight: '1.5',
                boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                animation: 'slideInUp 0.3s ease'
              }}
            >
              <div className="message-content">{msg.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatBody;
