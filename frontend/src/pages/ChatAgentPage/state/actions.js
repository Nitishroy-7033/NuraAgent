import { addMessage, setLoading, setSessions, setCurrentSession, setMessages } from './state';
import { streamChatCompletion } from './chatStreamClient';
import apiClient from '../../../context/apiClient';
import { API_ENDPOINTS } from '../../../configs/configs';

const DEFAULT_USER_ID = "sdf"; // As per request example

export const fetchSessions = (limit = 20) => async (dispatch) => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.sessions, {
      params: { userId: DEFAULT_USER_ID, limit }
    });
    dispatch(setSessions(response.data.sessions || []));
  } catch (error) {
    console.error('Failed to fetch sessions:', error);
  }
};

export const fetchChatHistory = (sessionId) => async (dispatch) => {
  if (!sessionId) return;
  dispatch(setLoading(true));
  try {
    const response = await apiClient.get(API_ENDPOINTS.chatHistory, {
      params: { sessionid: sessionId, pagesize: 20, currentpage: 1 }
    });
    const history = response.data.chats || [];
    // Map to UI format and reverse to chronological order
    const mappedHistory = history.map(chat => ({
      role: chat.role,
      text: chat.content,
      id: chat.created_at,
    })).reverse();
    dispatch(setMessages(mappedHistory));
  } catch (error) {
    console.error('Failed to fetch chat history:', error);
  } finally {
    dispatch(setLoading(false));
  }
};

export const createNewChat = (title = "New Chat") => async (dispatch) => {
  dispatch(setLoading(true));
  try {
    const response = await apiClient.post(API_ENDPOINTS.sessions, {
      title,
      userId: DEFAULT_USER_ID
    });
    const newSession = response.data;
    dispatch(setCurrentSession(newSession));
    dispatch(setMessages([])); // Clear messages for new session
    dispatch(fetchSessions()); // Refresh list
    return newSession;
  } catch (error) {
    console.error('Failed to create session:', error);
    return null;
  } finally {
    dispatch(setLoading(false));
  }
};

export const streamChatMessage = async ({
  message,
  sessionId = null,
  signal,
  onChunk,
  onEvent,
  onDone,
  onError,
}) =>
  streamChatCompletion({
    message,
    sessionId,
    signal,
    onToken: onChunk,
    onEvent,
    onDone,
    onError,
  });

export const sendChatMessage = (message, sessionId = null) => async (dispatch) => {
  dispatch(setLoading(true));

  dispatch(addMessage({ role: 'user', text: message }));

  try {
    let assistantText = '';

    await streamChatMessage({
      message,
      sessionId,
      onChunk: (chunk) => {
        assistantText += chunk;
      },
    });

    dispatch(
      addMessage({
        role: 'assistant',
        text: assistantText || 'No response received from JARVIS.',
      })
    );
  } catch (error) {
    console.error('Failed to send message:', error);
    dispatch(
      addMessage({
        role: 'assistant',
        text: 'Sorry, I am having trouble connecting to JARVIS.',
      })
    );
  } finally {
    dispatch(setLoading(false));
  }
};
