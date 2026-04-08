import React, { useState, useEffect } from 'react';
import './Sidebar.css';
import { useTheme } from '../../../context/ThemeContext';
import { useSelector, useDispatch } from 'react-redux';
import { fetchSessions, createNewChat } from '../state/actions';
import { setCurrentSession, setMessages } from '../state/state';

const Sidebar = () => {
    const { theme, toggleTheme } = useTheme();
    const [isCollapsed, setIsCollapsed] = useState(false);
    const dispatch = useDispatch();
    const { sessions, currentSession } = useSelector((state) => state.chat);

    useEffect(() => {
        dispatch(fetchSessions());
    }, [dispatch]);

    const toggleCollapse = () => {
        setIsCollapsed(!isCollapsed);
    };

    const handleNewChat = () => {
        dispatch(setMessages([]));
        dispatch(setCurrentSession(null));
    };

    const handleSelectSession = (session) => {
        dispatch(setCurrentSession(session));
        dispatch(setMessages([])); // For now, we don't fetch history, but clear to show it's a different context
    };

    return (
        <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
            <div className="sidebar-header">
                <div className="logo-area">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 4C16.41 4 20 7.59 20 12C20 13.53 19.57 14.97 18.83 16.19L16.22 13.58C16.71 13.1 17 12.44 17 11.72C17 10.22 15.78 9 14.28 9H13V7.72C13 6.22 11.78 5 10.28 5H9.72C8.22 5 7 6.22 7 7.72V9H5.5V10.5H7V13.5H5.5V15H7V16.28C7 17.78 8.22 19 9.72 19H10.28C11.78 19 13 17.78 13 16.28V15H14.28C15.78 15 17 16.22 17 17.72V18.19C15.71 19.33 14.1 20 12.31 20H11.69C9.9 20 8.29 19.33 7 18.19V17.72C7 16.22 8.22 15 9.72 15H11V16.28C11 17.78 12.22 19 13.72 19H14.28C15.78 19 17 17.78 17 16.28V15.54L19.54 18.08C18.42 19.28 16.8 20 15 20H9C7.2 20 5.58 19.28 4.46 18.08L7 15.54V15H5.5V13.5H7V10.5H5.5V9H7V7.72C7 6.22 8.22 5 9.72 5H10.28C11.78 5 13 6.22 13 7.72V9H14.28C15.78 9 17 10.22 17 11.72C17 12.44 16.71 13.1 16.22 13.58L18.83 16.19C19.57 14.97 20 13.53 20 12C20 7.59 16.41 4 12 4V4Z" fill="var(--primary-orange)"/>
                    </svg>
                    {!isCollapsed && <span className="logo-text">Cognivo</span>}
                </div>
                <button className="collapse-btn" onClick={toggleCollapse}>
                    {isCollapsed ? (
                         <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 17 4 12 9 7"/><polyline points="16 17 11 12 16 7"/></svg>
                    ) : (
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="13 17 18 12 13 7"/><polyline points="6 17 11 12 6 7"/></svg>
                    )}
                </button>
            </div>

            <button className="new-chat-btn" onClick={handleNewChat}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                {!isCollapsed && (
                    <>
                        New Chat
                        <span className="shortcut">⌘ N</span>
                    </>
                )}
            </button>

            <div className="history-sections">
                {!isCollapsed && (
                    <>
                        <div className="history-category">RECENT CHATS</div>
                        {sessions && sessions.length > 0 ? (
                            sessions.map((session) => (
                                <div 
                                    key={session.id || session._id} 
                                    className={`history-item ${currentSession?.id === (session.id || session._id) ? 'active' : ''}`}
                                    onClick={() => handleSelectSession(session)}
                                    title={session.title}
                                >
                                    {session.title || "Untitled Chat"}
                                </div>
                            ))
                        ) : (
                            <div className="history-empty">No recent chats</div>
                        )}
                    </>
                )}
            </div>

            <div className="sidebar-footer">
                <div className="settings-item" onClick={toggleTheme} title={isCollapsed ? (theme === 'light' ? 'Dark Mode' : 'Light Mode') : ''}>
                    {theme === 'light' ? (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                    ) : (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                    )}
                    {!isCollapsed && (theme === 'light' ? 'Dark Mode' : 'Light Mode')}
                </div>
                <div className="settings-item" title={isCollapsed ? 'Settings' : ''}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 -1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                    {!isCollapsed && 'Settings'}
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
