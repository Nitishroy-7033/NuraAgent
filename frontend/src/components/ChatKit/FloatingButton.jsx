import React from 'react';

const FloatingButton = ({ onClick, isOpen, name = "ChatKit" }) => {
  return (
    <button 
      className={`chatkit-fab ${isOpen ? 'open' : ''}`}
      onClick={onClick}
      aria-label="Toggle Chat"
    >
      <div className="icon">
        {isOpen ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        )}
      </div>
      <span className="chatkit-fab-label">{name}</span>
    </button>
  );
};

export default FloatingButton;
