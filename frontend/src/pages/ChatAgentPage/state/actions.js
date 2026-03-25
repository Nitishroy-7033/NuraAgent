import { addMessage, setLoading } from './state';

export const sendChatMessage = (message) => async (dispatch) => {
  dispatch(setLoading(true));
  
  // Optimistic update
  dispatch(addMessage({ role: 'user', content: message }));

  try {
    // Note: Assuming backend is at http://localhost:8000
    const response = await fetch('http://localhost:8000/chat/completion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: message }),
    });
    
    const data = await response.json();
    dispatch(addMessage({ role: 'assistant', content: data.response }));
  } catch (error) {
    console.error('Failed to send message:', error);
    dispatch(addMessage({ role: 'assistant', content: 'Sorry, I am having trouble connecting to the brain.' }));
  } finally {
    dispatch(setLoading(false));
  }
};
