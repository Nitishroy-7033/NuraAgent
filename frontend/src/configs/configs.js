const APP_CONFIG = {
  api: {
    baseURL: 'http://localhost:8000',
    timeoutMs: 120000,
    endpoints: {
      chatStream: 'agent/chat/stream',
      sessions: 'sessions',
      chatHistory: 'chat-history',
    },
  },
};

export const API_BASE_URL = APP_CONFIG.api.baseURL;
export const API_ENDPOINTS = APP_CONFIG.api.endpoints;

export default APP_CONFIG;
