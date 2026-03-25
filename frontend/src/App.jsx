import { Routes, Route, useNavigate } from 'react-router-dom';
import "./App.css";
import { Button, Box } from 'mango-ui-kit';
import HomePage from './pages/HomePage/HomePage';
import ChatAgentPage from './pages/ChatAgentPage/ChatAgentPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/chat" element={<ChatAgentPage />} />
    </Routes>
  );
}

export default App;

