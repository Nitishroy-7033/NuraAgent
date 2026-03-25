import React, { useState, useEffect, useRef } from 'react';
import './VoiceRecordingArea.css';
import { useVoiceRecorder } from './useVoiceRecorder';

function VoiceRecordingArea({ onCancel, onStop }) {
  const [recordingTime, setRecordingTime] = useState(0);
  const timerRef = useRef(null);

  const { startRecording, stopRecording, cancelRecording, error } = useVoiceRecorder((blob, url) => {
    console.log("Recorded Audio Blob:", blob);
    if (onStop) onStop(blob, url);
  });

  useEffect(() => {
    // Start actual mic recording on mount
    startRecording();
    
    setRecordingTime(0);
    timerRef.current = setInterval(() => {
      setRecordingTime(prev => prev + 1);
    }, 1000);
    
    return () => { 
        if (timerRef.current) clearInterval(timerRef.current);
        cancelRecording(); // Cleanup stream on unmount
    };
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStop = () => {
    stopRecording();
  };

  const handleCancelAction = () => {
    cancelRecording();
    if (onCancel) onCancel();
  };

  return (
    <div className="chat-input-box recording-mode">
      <div className="recording-header">
        {error ? <span className="error-text">{error}</span> : "Go ahead, record a quick note"}
      </div>
      <div className="recording-body">
        <button className="cancel-pill" onClick={handleCancelAction}>Cancel</button>
        
        <div className="timer-section">
           {!error && <div className="red-dot"></div>}
           <span className="timer-text">0:{formatTime(recordingTime)}</span>
        </div>

        <div className="recording-right-actions">
           <button className="icon-btn-round-light">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10 15 10 9"/><path d="M14 15 14 9"/></svg>
           </button>
           <button className="confirm-btn-blue" onClick={handleStop} disabled={!!error}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3"><polyline points="20 6 9 17 4 12"/></svg>
           </button>
        </div>
      </div>
    </div>
  );
}

export default VoiceRecordingArea;
