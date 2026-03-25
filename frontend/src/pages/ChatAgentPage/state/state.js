import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  currentSession: null,
  sessions: [],
  loading: false,
  messages: [],
  query: "",
};

const chatAgentSlice = createSlice({
  name: 'chatAgent',
  initialState,
  reducers: {
    setQuery: (state, action) => {
      state.query = action.payload;
    },
    setCurrentSession: (state, action) => {
      state.currentSession = action.payload;
    },
    setMessages: (state, action) => {
      state.messages = action.payload;
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    clearChat: (state) => {
      state.messages = [];
      state.currentSession = null;
    }
  },
});

export const { 
  setQuery, 
  setCurrentSession, 
  setMessages, 
  addMessage, 
  setLoading, 
  clearChat 
} = chatAgentSlice.actions;

export default chatAgentSlice.reducer;
