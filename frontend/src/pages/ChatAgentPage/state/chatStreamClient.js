const STREAM_URL = 'http://localhost:8000/chat/stream';

const normalizeDataLine = (line) => {
  const raw = line.slice(5);
  return raw.startsWith(' ') ? raw.slice(1) : raw;
};

const parseSseEvent = (eventText) => {
  const lines = eventText.split('\n');
  const dataLines = lines.filter((line) => line.startsWith('data:'));
  if (dataLines.length === 0) {
    return null;
  }

  const dataPayload = dataLines.map(normalizeDataLine).join('\n');
  if (dataPayload === '[DONE]') {
    return { done: true };
  }

  try {
    return { data: JSON.parse(dataPayload) };
  } catch (error) {
    return { error: 'Invalid stream payload received.' };
  }
};

export const streamChatCompletion = async ({
  query,
  threadId = null,
  onToken,
  onDone,
  onError,
  signal,
}) => {
  const response = await fetch(STREAM_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({
      query,
      thread_id: threadId,
    }),
    signal,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || 'Failed to connect to the stream.');
  }

  if (!response.body) {
    throw new Error('Streaming response body was empty.');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let streamDone = false;

  while (!streamDone) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const normalized = buffer.replace(/\r\n/g, '\n');
    const parts = normalized.split('\n\n');
    buffer = parts.pop() || '';

    for (const part of parts) {
      const parsed = parseSseEvent(part.trim());
      if (!parsed) {
        continue;
      }

      if (parsed.done) {
        streamDone = true;
        onDone?.();
        break;
      }

      if (parsed.error) {
        onError?.(parsed.error);
        continue;
      }

      if (parsed.data?.error) {
        onError?.(parsed.data.error);
        continue;
      }

      if (typeof parsed.data?.text === 'string') {
        onToken?.(parsed.data.text);
      }
    }
  }
};
