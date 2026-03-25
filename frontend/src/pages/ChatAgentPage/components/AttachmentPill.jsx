import React from 'react';
import './AttachmentPill.css';

function AttachmentPill({ 
    attachment, 
    onRemove, 
    onTogglePlay, 
    isPlaying 
}) {
    const { id, type, name, url } = attachment;

    return (
        <div className={`attachment-pill type-${type}`}>
            <div className={`attachment-icon-c ${type}`}>
                {type === 'audio' && <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>}
                {type === 'image' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><circle cx="8.5" cy="8.5" r="1.5" /><polyline points="21 15 16 10 5 21" /></svg>}
                {type === 'file' && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>}
            </div>
            
            <span className="attachment-name" title={name}>{name}</span>
            
            <div className="attachment-controls">
                {type === 'audio' && (
                    <button className="attach-action-btn" onClick={() => onTogglePlay(id)}>
                        {isPlaying ? (
                             <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                        ) : (
                             <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                        )}
                    </button>
                )}
                <button className="attach-action-btn remove-btn" onClick={() => onRemove(id)}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
            </div>
        </div>
    );
}

export default AttachmentPill;
