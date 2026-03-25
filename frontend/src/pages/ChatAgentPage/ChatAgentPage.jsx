import { Button, Box } from "mango-ui-kit";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { setCurrentSession } from "./state/state"; // Import from the new location
import { sendChatMessage } from "./state/actions"; // Use actions thunk

function ChatAgentPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { currentSession, loading, messages } = useSelector((state) => state.chat);

  const startSession = () => {
    dispatch(setCurrentSession({ id: Date.now() }));
    dispatch(sendChatMessage("Hello, test session!"));
  };

  return (
    <Box className="app-container">
      <Button variant="ghost" onClick={() => navigate('/')}>← Back</Button>
      <h1>Chat with JARVIS</h1>
      <p>Status: {loading ? 'Thinking...' : 'Ready'}</p>
      
      {currentSession ? (
        <Box>
           <p>Last Message: {messages[messages.length - 1]?.content}</p>
        </Box>
      ) : (
        <Button color="primary" onClick={startSession}>Start New Chat</Button>
      )}
    </Box>
  );
}

export default ChatAgentPage;


