import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  messages: [],
  systemState: 'Online', // Online, Processing, Error
};

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessages: (state, action) => {
      // action.payload should be an array of message objects
      state.messages = [...state.messages, ...action.payload];
    },
    updateLastAssistantMessage: (state, action) => {
      // action.payload is the new content string
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === 'assistant') {
        last.content = action.payload;
      }
    },
    setSystemState: (state, action) => {
      state.systemState = action.payload;
    },
    clearHistory: (state) => {
      state.messages = initialState.messages;
      state.systemState = 'Online';
    },
  },
});

export const { addMessages, updateLastAssistantMessage, setSystemState, clearHistory } = chatSlice.actions;

export default chatSlice.reducer;
