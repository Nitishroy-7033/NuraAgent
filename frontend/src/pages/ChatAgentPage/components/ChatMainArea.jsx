import React from 'react';
import './ChatMainArea.css';
import ChatInputField from './ChatInputField';

const ChatMainArea = () => {
    const quickActions = [
        {
            title: "Summarize Text",
            desc: "Turn long articles into easy summaries.",
            icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="7" y1="8" x2="17" y2="8" /><line x1="7" y1="12" x2="17" y2="12" /><line x1="7" y1="16" x2="13" y2="16" /></svg>
        },
        {
            title: "Creative Writing",
            desc: "Generate stories, blog posts, or fresh content ideas in seconds.",
            icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" /></svg>
        },
        {
            title: "Answer Questions",
            desc: "Ask me anything—from facts to advice—and get instant answers.",
            icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 1 1-7.6-11.7 8.38 8.38 0 0 1 3.8.9L21 3l-1.5 6.5Z" /><circle cx="12" cy="12" r="3" /></svg>
        }
    ];

    return (
        <main className="chat-main">
            {/* <header className="chat-header">
                <div className="model-selector">
                    <span className="model-name">Cognivo Core v1</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9"/></svg>
                </div>
                <div className="header-actions">
                    <div className="upgrade-pill">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff7c33" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                        Upgrade <span>free plan to full access</span>
                    </div>
                    <div className="header-icons">
                         <button className="icon-btn-round">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
                        </button>
                        <button className="icon-btn-round">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                        </button>
                        <button className="share-btn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
                            Share
                        </button>
                    </div>
                </div>
            </header> */}

            <div className="chat-content">
                <div className="welcome-section">
                    <img src="https://cdn-icons-png.flaticon.com/512/1000/1000845.png" alt="Cognivo" className="welcome-logo" />
                    <h1>Let's start a smart conversation</h1>
                </div>

                <div className="input-pnl">
                    <div className="suggested-questions">
                        <span className="suggestion-label">Suggested questions:</span>
                        <div className="suggestion-pills">
                            <button className="suggestion-pill">Create customise Form? ✨</button>
                            <button className="suggestion-pill">Get top 10 high rist account for last 7 days✨</button>
                            <button className="suggestion-pill">How to connect flow? ✨</button>
                        </div>
                    </div>
                    <ChatInputField />
                </div>

                <div className="quick-actions">
                    {quickActions.map((action, idx) => (
                        <div key={idx} className="action-card">
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
