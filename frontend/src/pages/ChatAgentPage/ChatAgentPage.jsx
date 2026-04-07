import React, { useEffect, useRef, useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatMainArea from './components/ChatMainArea';
import { streamChatMessage } from './state/actions';

function ChatAgentPage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const activeStreamRef = useRef(null);

  const updateAssistantMessage = (assistantMsgId, updater) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === assistantMsgId ? updater(m) : m))
    );
  };

  useEffect(() => {
    return () => {
      if (activeStreamRef.current) {
        activeStreamRef.current.abort();
      }
    };
  }, []);

  const handleMessage = async (msg) => {
    if (loading) {
      return;
    }

    const newUserMsg = {
      role: 'user',
      text: msg.text || 'Voice message / No text',
      attachments: msg.attachments || [],
      selectedTools: msg.selectedTools || [],
    };

    const assistantMsgId = Date.now();

    setMessages((prev) => [
      ...prev,
      newUserMsg,
      {
        id: assistantMsgId,
        role: 'assistant',
        status: 'Connecting to JARVIS...',
        text: '',
        thinking: '',
      },
    ]);

    if (activeStreamRef.current) {
      activeStreamRef.current.abort();
    }

    const controller = new AbortController();
    activeStreamRef.current = controller;
    setLoading(true);

    try {
      await streamChatMessage({
        message: newUserMsg.text,
        sessionId: null,
        signal: controller.signal,
        onEvent: (event) => {
          if (!event || (event.type !== 'start' && event.type !== 'thinking')) {
            return;
          }

          updateAssistantMessage(assistantMsgId, (current) => {
            const statusText =
              typeof event.content === 'string' && event.content.trim()
                ? event.content
                : 'JARVIS is responding...';
            const nextThinking =
              typeof event.content === 'string' && event.content.trim()
                ? current.thinking
                  ? `${current.thinking}\n${event.content}`
                  : event.content
                : current.thinking;

            return {
              ...current,
              status: statusText,
              thinking: nextThinking,
            };
          });
        },
        onChunk: (token) => {
          updateAssistantMessage(assistantMsgId, (current) => ({
            ...current,
            text: `${current.text || ''}${token}`,
          }));
        },
        onDone: () => {
          updateAssistantMessage(assistantMsgId, (current) => ({
            ...current,
            status: null,
          }));
        },
        onError: (error) => {
          updateAssistantMessage(assistantMsgId, (current) => ({
            ...current,
            status: null,
            text: current.text
              ? `${current.text}\n\nJARVIS error: ${error}`
              : `JARVIS error: ${error}`,
          }));
        },
      });
    } catch (error) {
      if (error?.name !== 'AbortError' && error?.name !== 'CanceledError') {
        updateAssistantMessage(assistantMsgId, (current) => ({
          ...current,
          status: null,
          text: current.text
            ? `${current.text}\n\nJARVIS error: Unable to connect to the stream.`
            : 'JARVIS error: Unable to connect to the stream.',
        }));
      }
    } finally {
      if (activeStreamRef.current === controller) {
        activeStreamRef.current = null;
      }
      setLoading(false);
    }
  };

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

  const tools = [
    // { position: 'left', className: 'deeper-research-btn', label: 'Deeper Research', selectable: true, icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v4" /><path d="m19.07 4.93-2.83 2.83" /><path d="M22 12h-4" /><path d="m19.07 19.07-2.83-2.83" /><path d="M12 22v-4" /><path d="m4.93 19.07 2.83-2.83" /><path d="M2 12h4" /><path d="m4.93 4.93 2.83 2.83" /></svg>, onClick: () => console.log('Research') },
    // { position: 'left', label: 'Upload Image', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><circle cx="8.5" cy="8.5" r="1.5" /><polyline points="21 15 16 10 5 21" /></svg>, onClick: () => console.log('Image') },
    // { position: 'left', label: 'Idea Generation', selectable: true, icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18h6" /><path d="M10 22h4" /><path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z" /></svg>, onClick: () => console.log('Idea') },
    // { position: 'left', label: 'Idea Generatio', selectable: true, icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18h6" /><path d="M10 22h4" /><path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z" /></svg>, onClick: () => console.log('Idea') },
    // { position: 'right', label: 'Code Snippets', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="4" width="16" height="16" rx="2" /><rect x="9" y="9" width="6" height="6" /><line x1="9" y1="1" x2="9" y2="4" /><line x1="15" y1="1" x2="15" y2="4" /><line x1="9" y1="20" x2="9" y2="23" /><line x1="15" y1="20" x2="15" y2="23" /><line x1="20" y1="9" x2="23" y2="9" /><line x1="20" y1="15" x2="23" y2="15" /><line x1="1" y1="9" x2="4" y2="9" /><line x1="1" y1="15" x2="4" y2="15" /></svg>, onClick: () => console.log('Code') },
    // { position: 'right', label: 'Global Search', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="2" y1="12" x2="22" y2="12" /><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" /></svg>, onClick: () => console.log('Global') },
    { position: 'right', label: 'Attach Files', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" /></svg>, onClick: () => console.log('Attach') },
    { position: 'right', className: 'icon-action mic-icon', label: 'Voice Input', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line x1="12" y1="19" x2="12" y2="23" /><line x1="8" y1="23" x2="16" y2="23" /></svg>, onClick: () => console.log('Mic') }
  ];

  const promoConfig = {
    text: "Upgrade to connect all your tools to Cognivo",
    icons: [
      { text: 'G', bg: '#4285F4' },
      { text: 'S', bg: '#E01E5A' },
      { text: 'T', bg: '#1DA1F2' },
      { text: 'L', bg: '#0a66c2' },
      { text: '>', bg: '#ff7c33' }
    ]
  };

  return (
    <div className="app-container" style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />
      <ChatMainArea
        messages={messages}
        onSendMessage={handleMessage}
        loading={loading}
        suggestions={[
          "Analyze the latest market trends",
          "Explain quantum computing simply",
          "Write a Python script for data scraping"
        ]}
        quickActions={quickActions}
        tools={tools}
        promoConfig={promoConfig}
      />
    </div>
  );
}

export default ChatAgentPage;
