import { Routes, Route, useNavigate } from 'react-router-dom';
import "./App.css";
import { Button, Box } from 'mango-ui-kit';
import ChatAgentPage from './pages/ChatAgentPage/ChatAgentPage';

function App() {
  const navigate = useNavigate();

  return (
    <Routes>
      <Route path="/" element={
        <Box className="welcome-container">
          <h1>Welcome to NuraAgent</h1>
          <p>Your AI assistant for seamless interactions.</p>
          <Button color="primary" onClick={() => navigate('/chat')}>Get Started</Button>
        </Box>
      } />
      <Route path="/chat" element={<ChatAgentPage />} />
    </Routes>
  );
}

export default App;

