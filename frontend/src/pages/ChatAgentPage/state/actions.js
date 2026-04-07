import { addMessage, setLoading } from './state';
import { streamChatCompletion } from './chatStreamClient';

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

export const sendChatMessage = (message) => async (dispatch) => {
  dispatch(setLoading(true));

  dispatch(addMessage({ role: 'user', text: message }));

  try {
    let assistantText = '';

    await streamChatMessage({
      message,
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
