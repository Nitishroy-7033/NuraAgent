import React, { useState, useRef, useEffect } from 'react';
import './ChatInputField.css';
import VoiceRecordingArea from './VoiceRecordingArea';
import AttachmentPill from './AttachmentPill';

function ChatInputField({ 
  onSendMessage, 
  loading, 
  placeholder = "Ask me anything...",
  actions = [],
  showPromo: initialShowPromo = true,
  promoConfig = null,
  enableMic = true,
  onRecordingComplete = (data) => console.log('Recording complete:', data)
}) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const audioRefs = useRef({});
  const [showPromo, setShowPromo] = useState(initialShowPromo);
  const [isRecording, setIsRecording] = useState(false);
  const [attachments, setAttachments] = useState([]);
  const [playingAudioId, setPlayingAudioId] = useState(null);

  useEffect(() => {
    if (textareaRef.current && !isRecording) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message, isRecording, attachments]);

  const handleSend = () => {
    if ((message.trim() || attachments.length > 0) && !loading) {
      if (onSendMessage) {
        onSendMessage({
            text: message.trim(),
            attachments: attachments
        });
      }
      setMessage('');
      setAttachments([]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startRecording = () => {
    setIsRecording(true);
  };

  const stopRecording = (submit = true, blob = null, url = null) => {
    setIsRecording(false);
    if (submit && blob) {
      const id = Date.now();
      const newAudio = { 
          id,
          type: 'audio',
          blob, 
          url, 
          name: `Voice note ${new Date().toLocaleTimeString([], {minute: '2-digit', second: '2-digit'})}` 
      };
      setAttachments(prev => [...prev, newAudio]);
      onRecordingComplete(newAudio);
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    const newAttachments = files.map(file => {
        const type = file.type.startsWith('image/') ? 'image' : 'file';
        return {
            id: Math.random().toString(36).substr(2, 9),
            type,
            file,
            url: URL.createObjectURL(file),
            name: file.name
        };
    });
    setAttachments(prev => [...prev, ...newAttachments]);
    e.target.value = null; // Reset input
  };

  const togglePlayAudio = (id) => {
    const audio = audioRefs.current[id];
    if (audio) {
        if (playingAudioId === id) {
            audio.pause();
            setPlayingAudioId(null);
        } else {
            // Stop other playing audio if any
            if (playingAudioId && audioRefs.current[playingAudioId]) {
                audioRefs.current[playingAudioId].pause();
            }
            audio.play();
            setPlayingAudioId(id);
        }
    }
  };

  const removeAttachment = (id) => {
    setAttachments(prev => prev.filter(a => a.id !== id));
    if (playingAudioId === id) setPlayingAudioId(null);
  };

  const leftActions = actions.filter(a => a.position === 'left');
  const rightActions = actions.filter(a => a.position === 'right');

  // Handle specific tool clicks
  const handleActionClick = (action) => {
    if (action.label === 'Voice Input') {
      startRecording();
    } else if (action.label === 'Upload Image' || action.label === 'Attach Files') {
      fileInputRef.current.click();
    } else if (action.onClick) {
      action.onClick();
    }
  };

  if (isRecording) {
    return (
      <VoiceRecordingArea 
        onCancel={() => stopRecording(false)} 
        onStop={(blob, url) => stopRecording(true, blob, url)} 
      />
    );
  }

  return (
    <div className={`chat-input-box ${showPromo && promoConfig ? 'promo-visible' : 'promo-hidden'}`}>
      
      <input 
        type="file" 
        ref={fileInputRef} 
        style={{display: 'none'}} 
        multiple 
        onChange={handleFileChange}
      />

      {attachments.length > 0 && (
        <div className="attachments-area">
            {attachments.map((a) => (
                <React.Fragment key={a.id}>
                    <AttachmentPill 
                        attachment={a}
                        isPlaying={playingAudioId === a.id}
                        onRemove={removeAttachment}
                        onTogglePlay={togglePlayAudio}
                    />
                    {a.type === 'audio' && (
                        <audio 
                            ref={el => audioRefs.current[a.id] = el} 
                            src={a.url} 
                            onEnded={() => setPlayingAudioId(null)}
                            style={{display: 'none'}}
                        />
                    )}
                </React.Fragment>
            ))}
        </div>
      )}

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
              onClick={() => handleActionClick(action)}
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
              onClick={() => handleActionClick(action)}
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
