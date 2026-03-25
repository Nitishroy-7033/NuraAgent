import React from 'react';
import './ChatMainArea.css';
import ChatInputField from './ChatInputField';

const ChatMainArea = ({ 
    suggestions = [],
    quickActions = [],
    tools = [],
    onSendMessage = (msg) => console.log('Sending message:', msg),
    loading = false,
    promoConfig = null
}) => {
    return (
        <main className="chat-main">
            <div className="chat-content">
                <div className="welcome-section">
                    <img src="https://cdn-icons-png.flaticon.com/512/1000/1000845.png" alt="Cognivo" className="welcome-logo" />
                    <h1>Let's start a smart conversation</h1>
                </div>

                <div className="input-pnl">
                    {suggestions.length > 0 && (
                        <div className="suggested-questions">
                            <span className="suggestion-label">Suggested questions:</span>
                            <div className="suggestion-pills">
                                {suggestions.map((s, idx) => (
                                    <button key={idx} className="suggestion-pill" onClick={() => onSendMessage(s)}>{s}</button>
                                ))}
                            </div>
                        </div>
                    )}
                    <ChatInputField 
                        onSendMessage={onSendMessage} 
                        loading={loading}
                        actions={tools}
                        promoConfig={promoConfig}
                    />
                </div>

                <div className="quick-actions">
                    {quickActions.map((action, idx) => (
                        <div key={idx} className="action-card" onClick={() => onSendMessage(action.title)}>
                            <div className="action-icon">{action.icon}</div>
                            <div className="action-text">
                                <h3>{action.title}</h3>
                                <p>{action.desc}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* <footer className="chat-footer">
                <span className="footer-disclaimer">Cognivo can make mistakes. Check important info. See <b>Cookie Preferences</b>.</span>
                <div className="footer-icons">
                    <button className="icon-btn-plain">
                         <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h10"/></svg>
                    </button>
                    <button className="icon-btn-plain">
                         <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    </button>
                </div>
            </footer> */}
        </main>
    );
};

export default ChatMainArea;
