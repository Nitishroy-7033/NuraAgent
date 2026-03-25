import React, { useState } from 'react';
import './ToolCallCard.css';

const ToolCallCard = ({ tool }) => {
    const { name, status, input, output, statusText } = tool;
    const [expanded, setExpanded] = useState(false);

    const getStatusConfig = (status) => {
        switch (status) {
            case 'processing': return { label: 'Processing', color: '#4285F4', bg: 'rgba(66, 133, 244, 0.1)', icon: 'spinner' };
            case 'ready': return { label: 'Ready', color: '#FF7C33', bg: 'rgba(255, 124, 51, 0.1)', icon: 'settings' };
            case 'completed': return { label: 'Completed', color: '#34A853', bg: 'rgba(52, 168, 83, 0.1)', icon: 'check' };
            case 'error': return { label: 'Error', color: '#EA4335', bg: 'rgba(234, 67, 53, 0.1)', icon: 'error' };
            default: return { label: 'Done', color: '#34A853', bg: 'rgba(52, 168, 83, 0.1)', icon: 'check' };
        }
    };

    const config = getStatusConfig(status?.toLowerCase());

    const renderIcon = (type) => {
        if (type === 'spinner') return <div className="tool-spinner"></div>;
        if (type === 'settings') return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1Z"/></svg>;
        if (type === 'check') return <svg style={{color: '#34A853'}} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12"/></svg>;
        if (type === 'error') return <svg style={{color: '#EA4335'}} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>;
        return null;
    };

    return (
        <div className={`tool-call-card ${expanded ? 'expanded' : ''}`}>
            <div className="tool-card-header" onClick={() => setExpanded(!expanded)}>
                <div className="tool-info">
                   <div className="tool-icon-wrap" style={{color: config.color}}>
                       {renderIcon(config.icon)}
                   </div>
                   <span className="tool-name">{name}</span>
                   <div className="status-pill" style={{backgroundColor: config.bg, color: config.color}}>
                       {config.label}
                   </div>
                </div>
                <svg className={`chevron ${expanded ? 'up' : ''}`} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m6 9 6 6 6-6"/></svg>
            </div>

            {expanded && (
                <div className="tool-card-body">
                    {input && (
                        <div className="tool-section">
                            <label>Input</label>
                            <div className="tool-code-block">
                                {Object.entries(input).map(([key, val]) => (
                                    <div key={key} className="code-line">
                                        <span className="key">{key}:</span> <span className="val">{String(val)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {output && (
                        <div className="tool-section">
                            <label>Output</label>
                            <pre className="tool-output-pre">
                                {JSON.stringify(output, null, 2)}
                            </pre>
                        </div>
                    )}

                    {statusText && <div className="tool-status-msg">{statusText}</div>}
                </div>
            )}
        </div>
    );
};

export default ToolCallCard;
