import React, { useState } from 'react';
import './ChatMessage.css';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import AttachmentPill from './AttachmentPill';
import ToolCallCard from './ToolCallCard';

const ChatMessage = ({ message }) => {
    const { role, text, attachments = [], selectedTools = [], status, thinking, toolCalls = [], resources = [] } = message;
    const [thoughtExpanded, setThoughtExpanded] = useState(false);

    if (role === 'user') {
        return (
            <div className="message-row user">
                <div className="message-content user">
                    {attachments.length > 0 && (
                        <div className="user-attachments">
                            {attachments.map(a => (
                                <AttachmentPill key={a.id} attachment={a} onRemove={() => {}} />
                            ))}
                        </div>
                    )}
                    <div className="text-bubble">{text}</div>
                </div>
                <div className="user-avatar">
                   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                </div>
            </div>
        );
    }

    return (
        <div className="message-row assistant">
            <div className="assistant-container">
                {thinking && (
                    <div className="thought-block">
                        <button className="thought-header" onClick={() => setThoughtExpanded(!thoughtExpanded)}>
                            <svg className={thoughtExpanded ? 'rotated' : ''} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"/><path d="M12 12L12 16"/><path d="M12 8L12.01 8"/></svg>
                            <span>Thought</span>
                            <svg className={`chevron ${thoughtExpanded ? 'up' : ''}`} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m6 9 6 6 6-6"/></svg>
                        </button>
                        {thoughtExpanded && <div className="thought-content">{thinking}</div>}
                    </div>
                )}

                {toolCalls.length > 0 && (
                    <div className="tool-calls-list">
                        {toolCalls.map((tool, idx) => (
                            <ToolCallCard key={idx} tool={tool} />
                        ))}
                    </div>
                )}

                {status && (
                    <div className="status-indicator">
                        <div className="spinner-dot"></div>
                        <span>{status}</span>
                    </div>
                )}

                <div className="assistant-text-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
                </div>

                {resources.length > 0 && (
                    <div className="resources-section">
                        <div className="results-count">{resources.length} results</div>
                        <div className="resources-list">
                            {resources.map((res, idx) => (
                                <div key={idx} className="resource-item" title={res.preview || res.title}>
                                    <div className="res-icon">
                                        {res.type === 'file' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>}
                                        {res.type === 'link' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>}
                                    </div>
                                    <span className="res-title">{res.title}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatMessage;
