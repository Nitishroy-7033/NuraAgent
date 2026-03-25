import React from 'react';
import Sidebar from './components/Sidebar';
import ChatMainArea from './components/ChatMainArea';

function ChatAgentPage() {
  return (
    <div className="app-container" style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />
      <ChatMainArea />
    </div>
  );
}

export default ChatAgentPage;
