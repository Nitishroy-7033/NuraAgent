import React from 'react';

const ChatHistory = ({ isOpen, onClose, history = [], onHistorySelect }) => {
  return (
    <aside className={`chatkit-history-sidebar ${isOpen ? 'open' : ''}`}>
      <div className="chatkit-history-header">
        <h4>Chat History</h4>
        <button className="chatkit-header-btn" onClick={onClose} title="Close History">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div className="chatkit-history-list">
        {history.length > 0 ? (
          history.map((item, idx) => (
            <div 
              key={idx} 
              className="chatkit-history-item"
              onClick={() => onHistorySelect(item)}
            >
              <h5>{item.title}</h5>
              <span>{item.date}</span>
            </div>
          ))
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--chatkit-text-secondary)', fontSize: '13px' }}>
            No recent conversations.
          </div>
        )}
      </div>
    </aside>
  );
};

export default ChatHistory;
