import axios from 'axios';
import APP_CONFIG, { API_ENDPOINTS } from '../configs/configs';

const apiClient = axios.create({
  baseURL: APP_CONFIG.api.baseURL,
  timeout: APP_CONFIG.api.timeoutMs,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const postChatStream = ({
  message,
  sessionId = null,
  signal,
  onDownloadProgress,
}) =>
  apiClient.post(
    API_ENDPOINTS.chatStream,
    {
      message,
      session_id: sessionId,
    },
    {
      signal,
      responseType: 'text',
      headers: {
        Accept: 'text/event-stream',
      },
      onDownloadProgress,
    }
  );

export default apiClient;
