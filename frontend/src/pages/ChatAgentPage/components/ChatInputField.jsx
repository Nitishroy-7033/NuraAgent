import React, { useState, useRef, useEffect } from 'react';
import './ChatInputField.css';

function ChatInputField({ 
  onSendMessage, 
  loading, 
  placeholder = "Ask me anything...",
  actions = [],
  showPromo: initialShowPromo = true,
  promoConfig = null
}) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);
  const [showPromo, setShowPromo] = useState(initialShowPromo);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !loading) {
      if (onSendMessage) onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const leftActions = actions.filter(a => a.position === 'left');
  const rightActions = actions.filter(a => a.position === 'right');

  return (
    <div className={`chat-input-box ${showPromo && promoConfig ? 'promo-visible' : 'promo-hidden'}`}>
      <div className="chat-input-main">
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          placeholder={placeholder}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
        />
      </div>

      <div className="chat-input-actions">
        <div className="left-actions">
          {leftActions.map((action, idx) => (
            <button 
              key={idx} 
              className={action.className || 'icon-action'} 
              onClick={action.onClick}
              data-tooltip={action.label}
            >
              {action.icon}
              {action.label && action.className === 'deeper-research-btn' && <span>{action.label}</span>}
            </button>
          ))}
        </div>

        <div className="right-actions">
          {rightActions.map((action, idx) => (
            <button 
              key={idx} 
              className={action.className || 'icon-action'} 
              onClick={action.onClick}
              data-tooltip={action.label}
            >
              {action.icon}
              {action.label && action.className === 'deeper-research-btn' && <span>{action.label}</span>}
            </button>
          ))}
          
          <button 
            className="send-btn-orange" 
            onClick={handleSend}
            disabled={!message.trim() || loading}
          >
            <span>Send</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><line x1="22" y1="2" x2="11" y2="13"/><polyline points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </button>
        </div>
      </div>

      {showPromo && promoConfig && (
        <div className="upgrade-promo">
            <span>{promoConfig.text}</span>
            <div className="promo-right">
                <div className="tool-icons">
                    {promoConfig.icons?.map((icon, idx) => (
                      <div key={idx} className="tool-circle" style={{background: icon.bg}}>{icon.text}</div>
                    ))}
                </div>
                <button className="close-promo" onClick={() => setShowPromo(false)}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
            </div>
        </div>
      )}
    </div>
  );
}

export default ChatInputField;
