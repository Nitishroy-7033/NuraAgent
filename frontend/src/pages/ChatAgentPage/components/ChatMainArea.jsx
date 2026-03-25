import React, { useRef, useEffect } from 'react';
import './ChatMainArea.css';
import ChatInputField from './ChatInputField';
import ChatMessage from './ChatMessage';

const ChatMainArea = ({ 
    messages = [],
    suggestions = [],
    quickActions = [],
    tools = [],
    onSendMessage = (msg) => console.log('Sending message:', msg),
    loading = false,
    promoConfig = null
}) => {
    const inputRef = React.useRef(null);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSuggestionClick = (s) => {
        if (inputRef.current) {
            inputRef.current.setMessage(s);
            // Submit with small delay so the user sees it in the box
            setTimeout(() => {
                inputRef.current.triggerSend(s);
            }, 500);
        }
    };

    const hasMessages = messages.length > 0;

    return (
        <main className={`chat-main ${hasMessages ? 'has-history' : ''}`}>
            <div className={`chat-content ${hasMessages ? 'with-history' : ''}`} ref={scrollRef}>
                {!hasMessages && (
                    <div className="welcome-section">
                        <img src="https://cdn-icons-png.flaticon.com/512/1000/1000845.png" alt="Cognivo" className="welcome-logo" />
                        <h1>Let's start a smart conversation</h1>
                    </div>
                )}

                {hasMessages && (
                    <div className="messages-stream">
                        {messages.map((msg, idx) => (
                            <ChatMessage key={idx} message={msg} />
                        ))}
                    </div>
                )}

                <div className="input-pnl">
                    {!hasMessages && suggestions.length > 0 && (
                        <div className="suggested-questions">
                            <span className="suggestion-label">Suggested questions:</span>
                            <div className="suggestion-pills">
                                {suggestions.map((s, idx) => (
                                    <button key={idx} className="suggestion-pill" onClick={() => handleSuggestionClick(s)}>{s}</button>
                                ))}
                            </div>
                        </div>
                    )}
                    <ChatInputField 
                        ref={inputRef}
                        onSendMessage={onSendMessage} 
                        loading={loading}
                        actions={tools}
                        promoConfig={promoConfig}
                    />
                </div>

                {!hasMessages && (
                    <div className="quick-actions">
                        {quickActions.map((action, idx) => (
                            <div key={idx} className="action-card" onClick={() => handleSuggestionClick(action.title)}>
                                <div className="action-icon">{action.icon}</div>
                                <div className="action-text">
                                    <h3>{action.title}</h3>
                                    <p>{action.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
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
