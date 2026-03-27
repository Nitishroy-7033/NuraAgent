import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatKitToolCard = ({ tool }) => {
  const [expanded, setExpanded] = useState(false);
  const { name, icon, status = 'completed', input, output } = tool;

  const statusColors = {
    completed: { bg: '#34A85322', text: '#34A853' },
    processing: { bg: '#4285F422', text: '#4285F4' },
    error: { bg: '#EA433522', text: '#EA4335' }
  };

  const currentStatus = statusColors[status.toLowerCase()] || statusColors.completed;

  const renderInput = (data) => {
    if (typeof data !== 'object') return <span className="string">{data}</span>;
    return Object.entries(data).map(([k, v]) => (
      <div key={k}>
        <span className="key">{k}:</span> <span className="string">{String(v)}</span>
      </div>
    ));
  };

  const renderOutput = (data) => {
    if (typeof data !== 'object') return <span className="string">"{data}"</span>;
    return (
      <>
        <span className="bracket">{'{'}</span>
        {Object.entries(data).map(([k, v], i, arr) => (
          <div key={k} style={{ paddingLeft: '20px' }}>
            <span className="key">"{k}"</span>: <span className="string">"{String(v)}"</span>
            {i < arr.length - 1 && <span className="bracket">,</span>}
          </div>
        ))}
        <span className="bracket">{'}'}</span>
      </>
    );
  };

  return (
    <div className={`chatkit-tool-card ${expanded ? 'expanded' : ''}`}>
      <div className="chatkit-tool-header" onClick={() => setExpanded(!expanded)}>
        <div className="chatkit-tool-info">
          <div className="chatkit-tool-icon-wrapper">
             {icon || (
               <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
             )}
          </div>
          <span className="chatkit-tool-name">{name}</span>
          <span className="chatkit-tool-status-pill" style={{ backgroundColor: currentStatus.bg, color: currentStatus.text }}>
            {status}
          </span>
        </div>
        <svg 
          width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" 
          style={{ transform: expanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s', color: 'var(--chatkit-text-secondary)' }}
        >
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>

      {expanded && (
        <div className="chatkit-tool-body">
          {input && (
            <div className="chatkit-tool-section">
              <label>INPUT</label>
              <pre className="chatkit-tool-code input-mode">
                {renderInput(input)}
              </pre>
            </div>
          )}
          {output && (
            <div className="chatkit-tool-section">
              <label>OUTPUT</label>
              <pre className="chatkit-tool-code">
                {renderOutput(output)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const AssistantMessage = ({ message }) => {
  const { content, thinking, toolCalls = [], status, resources = [] } = message;
  const [isThoughtExpanded, setIsThoughtExpanded] = useState(false);

  return (
    <div className="chatkit-message agent">
      {thinking && (
        <div className="chatkit-thought-block">
          <button 
            className="chatkit-thought-header" 
            onClick={() => setIsThoughtExpanded(!isThoughtExpanded)}
          >
             <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2"/><path d="M12 21v2"/><path d="M4.22 4.22l1.42 1.42"/><path d="M18.36 18.36l1.42 1.42"/><path d="M1 12h2"/><path d="M21 12h2"/><path d="M4.22 19.78l1.42-1.42"/><path d="M18.36 5.64l1.42-1.42"/></svg>
             <span>Thought</span>
             <svg style={{ transform: isThoughtExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s', marginLeft: '4px' }} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </button>
          {isThoughtExpanded && <div className="chatkit-thought-content">{thinking}</div>}
        </div>
      )}

      {toolCalls.length > 0 && (
        <div className="chatkit-tool-section-wrapper">
          <div className="chatkit-tool-label" style={{ marginBottom: '12px' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <span>Tool Execution</span>
          </div>
          <div className="chatkit-tool-calls">
            {toolCalls.map((tool, idx) => (
              <ChatKitToolCard key={idx} tool={tool} />
            ))}
          </div>
        </div>
      )}

      {status && (
        <div className="chatkit-status-indicator">
          <div className="chatkit-spinner"></div>
          <span>{status}</span>
        </div>
      )}

      <div className="chatkit-message-markdown">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>

      {resources.length > 0 && (
        <div className="chatkit-resources-section">
          <div className="chatkit-results-header">{resources.length} results</div>
          <div className="chatkit-resource-list">
             {resources.map((res, idx) => (
               <div key={idx} className="chatkit-resource-item">
                 <div className="chatkit-resource-icon">
                    {res.type === 'video' ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                    )}
                 </div>
                 <span>{res.title}</span>
               </div>
             ))}
          </div>
        </div>
      )}
    </div>
  );
};

const ChatBody = ({ 
  messages = [], 
  agentName = "ChatAgent", 
  suggestions = [], 
  onSuggestionClick,
  messageContainerRef
}) => {
  const hasMessages = messages.length > 0;

  return (
    <div className="chatkit-body" ref={messageContainerRef}>
      {!hasMessages ? (
        <div className="chatkit-empty-state">
          <div className="chatkit-agent-avatar">
            <span>A</span>
          </div>
          <h1>{agentName}</h1>
          <p>How can I help you today?</p>
          
          {suggestions.length > 0 && (
            <div className="chatkit-suggestions">
              {suggestions.map((s, idx) => (
                <button 
                  key={idx} 
                  className="chatkit-suggestion-btn" 
                  onClick={() => onSuggestionClick(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="chatkit-messages">
          {messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            
            return (
              <div 
                key={idx} 
                className={`chatkit-message-wrapper ${isUser ? 'user' : 'agent'}`}
                style={{
                  alignSelf: isUser ? 'flex-end' : 'flex-start',
                  maxWidth: '95%',
                  display: 'flex',
                  flexDirection: 'column',
                  animation: 'slideInUp 0.3s ease'
                }}
              >
                {isUser ? (
                  <div 
                    className="chatkit-message user"
                    style={{
                      background: 'var(--chatkit-primary)',
                      color: 'white',
                      padding: '10px 16px',
                      borderRadius: '16px',
                      borderBottomRightRadius: '4px',
                      fontSize: '14px',
                      lineHeight: '1.5',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                    }}
                  >
                    {msg.content}
                  </div>
                ) : (
                  <div 
                    className="chatkit-message agent"
                    style={{
                      background: 'rgba(0,0,0,0)',
                      color: 'var(--chatkit-text)',
                      padding: '12px 0',
                      borderRadius: '0',
                      fontSize: '14.5px',
                      width: '100%'
                    }}
                  >
                    <AssistantMessage message={msg} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ChatBody;
