import React, { useState, useRef, useEffect } from 'react';
import './ChatKit.css';
import FloatingButton from './FloatingButton';
import ChatPopup from './ChatPopup';

const ChatKit = ({ 
  agentName = "ChatAgent", 
  initialMessages = [], 
  suggestions = [
    "Tell me about yourself",
    "What services do you offer?",
    "Can you help me with coding?"
  ],
  onSendMessage = (msg) => console.log('Sending message:', msg),
  onToggle = (isOpen) => console.log('Chat toggle:', isOpen)
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState(initialMessages);
  const [loading, setLoading] = useState(false);
  const messageContainerRef = useRef(null);

  const toggleChat = () => {
    const nextState = !isOpen;
    setIsOpen(nextState);
    if (onToggle) onToggle(nextState);
  };

  const handleSendMessage = async (content) => {
    // Add user message locally
    const userMessage = { role: 'user', content, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    
    setLoading(true);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    try {
      await onSendMessage(content);
      
      // Hardcoded Agent Responses
      let responseContent = "I'm here to help! What else would you like to know?";
      const lowerContent = content.toLowerCase();

      if (lowerContent.includes("deploy")) {
        responseContent = "I've started the deployment process for your new agent. It should be ready in a few moments!";
      } else if (lowerContent.includes("help") || lowerContent.includes("how")) {
        responseContent = "You can ask me to search the web, write code, or manage your ecosystem. Just let me know what you need!";
      } else if (lowerContent.includes("who") || lowerContent.includes("yourself")) {
        responseContent = "I am Nura Assistant, a next-gen AI interface built for the NuraAgent ecosystem.";
      }

      const agentMessage = { role: 'agent', content: responseContent, timestamp: new Date() };
      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
       console.error("Error sending message:", error);
    } finally {
       setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleNewChat = () => {
    setMessages([]);
    setIsOpen(true);
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messageContainerRef.current) {
        messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  return (
    <div className="chatkit-wrapper">
      <ChatPopup 
        isOpen={isOpen}
        agentName={agentName}
        messages={messages}
        suggestions={suggestions}
        onSuggestionClick={handleSuggestionClick}
        onSendMessage={handleSendMessage}
        onNewChat={handleNewChat}
        loading={loading}
        messageContainerRef={messageContainerRef}
        toggleChat={toggleChat}
      />
      
      {!isOpen && (
        <FloatingButton 
          isOpen={isOpen} 
          onClick={toggleChat} 
          name="ChatKit" 
        />
      )}
    </div>
  );
};

export default ChatKit;
