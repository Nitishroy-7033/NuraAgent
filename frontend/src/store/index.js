import { configureStore } from '@reduxjs/toolkit';
import chatAgentReducer from '../pages/ChatAgentPage/state/state';

export const store = configureStore({
  reducer: {
    chat: chatAgentReducer,
  },
});

