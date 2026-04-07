import { postChatStream } from '../../../context/apiClient';

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
  } catch {
    return { error: 'Invalid stream payload received.' };
  }
};

export const streamChatCompletion = async ({
  message,
  sessionId = null,
  onToken,
  onEvent,
  onDone,
  onError,
  signal,
}) => {
  const getResponseTextFromProgress = (progress) => {
    const target =
      progress?.event?.target ||
      progress?.event?.currentTarget ||
      progress?.target ||
      progress?.currentTarget;

    if (typeof target?.responseText === 'string') {
      return target.responseText;
    }

    if (typeof target?.response === 'string') {
      return target.response;
    }

    return '';
  };

  let consumedLength = 0;
  let buffer = '';
  let streamDone = false;
  let doneNotified = false;

  const notifyDone = (payload = null) => {
    if (!doneNotified) {
      doneNotified = true;
      onDone?.(payload);
    }
  };

  const processBufferedEvents = ({ flushRemainder = false } = {}) => {
    if (!buffer) {
      return;
    }

    const normalized = buffer.replace(/\r\n/g, '\n');
    const eventBlocks = normalized.split('\n\n');

    buffer = flushRemainder ? '' : eventBlocks.pop() || '';

    for (const block of eventBlocks) {
      const parsed = parseSseEvent(block.trim());
      if (!parsed) {
        continue;
      }

      if (parsed.done) {
        streamDone = true;
        notifyDone();
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

      onEvent?.(parsed.data);

      if (parsed.data?.type === 'done') {
        streamDone = true;
        notifyDone(parsed.data);
        break;
      }

      if (parsed.data?.type === 'chunk' && typeof parsed.data?.content === 'string') {
        onToken?.(parsed.data.content, parsed.data);
      } else if (typeof parsed.data?.text === 'string') {
        onToken?.(parsed.data.text, parsed.data);
      }
    }
  };

  try {
    await postChatStream({
      message,
      sessionId,
      signal,
      onDownloadProgress: (progress) => {
        if (streamDone) {
          return;
        }

        const responseText = getResponseTextFromProgress(progress);
        if (!responseText || responseText.length <= consumedLength) {
          return;
        }

        buffer += responseText.slice(consumedLength);
        consumedLength = responseText.length;
        processBufferedEvents();
      },
    });

    processBufferedEvents({ flushRemainder: true });

    if (!streamDone) {
      notifyDone();
    }
  } catch (error) {
    if (error?.name === 'CanceledError' || error?.name === 'AbortError') {
      throw error;
    }

    const errorMessage =
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      error?.message ||
      'Failed to connect to the stream.';

    throw new Error(errorMessage);
  }
};
