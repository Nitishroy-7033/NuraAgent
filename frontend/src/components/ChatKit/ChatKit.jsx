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
    
    // Simulate complex AI reasoning process
    const lowerContent = content.toLowerCase();
    
    // 1. Initial Empty Agent Message with thinking
    const agentMessageId = Date.now();
    const initialAgentMessage = { 
      id: agentMessageId,
      role: 'agent', 
      content: '', 
      thinking: 'Analyzing request and searching ecosystem resources...',
      status: 'Connecting to agent engine...',
      timestamp: new Date() 
    };
    setMessages(prev => [...prev, initialAgentMessage]);

    // 2. Transition through thinking/tool states
    await new Promise(resolve => setTimeout(resolve, 800));
    setMessages(prev => prev.map(m => m.id === agentMessageId ? {
      ...m,
      thinking: 'Thinking: Identified target command. Fetching configuration files...',
      status: 'Executing tools...'
    } : m));

    await new Promise(resolve => setTimeout(resolve, 1000));
    setMessages(prev => prev.map(m => m.id === agentMessageId ? {
      ...m,
      status: 'Generating project workflow...',
      toolCalls: [{ 
        name: 'MCP: Onboarding Demo', 
        status: 'Completed',
        input: { session_id: "7782-UX", extract_vision: true },
        output: { status: "success", summary: "Extracted 5 key vision points" },
        icon: <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><rect x="0" y="0" width="24" height="24" rx="4" fill="#0E71EB"/><path d="M18 16l-3-2.5V10.5l3-2.5v8zM6 8h8v8H6V8z" fill="white"/></svg>
      }]
    } : m));

    await new Promise(resolve => setTimeout(resolve, 1200));

    try {
      await onSendMessage(content);
      
      // Calculate response content based on prompts
      let responseContent = `## Shaping the AI Chat Experience

- During the session, the team presented the overall product vision focused on building a modern AI chat experience that feels intuitive and easy to use for end users.
- Key emphasis was placed on clarity of interaction, reducing cognitive load, and ensuring responses feel helpful, contextual, and trustworthy.

## Key Takeaways

1. The experience should scale from onboarding demos to advanced workflows without increasing complexity for the user.
2. The AI chat should serve as a primary interface for user interaction, prioritizing simplicity and clear intent recognition.`;

      let resources = [
        { title: "Customer Feedback: Aggregated Insights and Key Pain Points", type: "file" },
        { title: "Sales Performance: Pipeline Health and Conversion Metrics", type: "file" },
        { title: "Product Overview Session", type: "video" }
      ];

      if (lowerContent.includes("deploy")) {
        responseContent = `I have successfully initiated the deployment sequence for your agent. You can monitor the progress in the dashboard.

### Deployment Details
\`\`\`yaml
agent_id: dev-agent-01
target: prod-cluster
resources: 
  cpu: "2"
  memory: "4Gi"
\`\`\`

Is there anything else you want to configure?`;
        resources = [{ title: "Deployment Cluster Config", type: "file" }];
      }

      // Update the message with final content
      setMessages(prev => prev.map(m => m.id === agentMessageId ? {
        ...m,
        content: responseContent,
        resources: resources,
        status: null, 
        thinking: 'Analyzed the onboarding session notes and extracted key product vision milestones. Identified clear UX priorities for the chat interface.'
      } : m));

    } catch (error) {
       console.error("Error sending message:", error);
       setMessages(prev => prev.map(m => m.id === agentMessageId ? {
        ...m,
        content: "I encountered an error while processing your request.",
        status: 'Error'
      } : m));
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
