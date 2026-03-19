/**
 * API utility for Chat Agent
 */

const API_BASE_URL = 'http://localhost:8000';

export const streamChat = async (message, onChunk, onDone, onError) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) throw new Error('Network response was not ok');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      
      // Keep the last partial line (if any) in the buffer
      buffer = lines.pop();

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine) continue;

        if (trimmedLine.startsWith('data: ')) {
          const dataStr = trimmedLine.slice(6).trim();
          
          if (dataStr === '[DONE]') {
            if (onDone) onDone(fullContent);
            continue;
          }

          try {
            const data = JSON.parse(dataStr);
            if (data.text) {
              fullContent += data.text;
              if (onChunk) onChunk(data.text, fullContent);
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e, 'Raw string:', dataStr);
          }
        }
      }
    }
  } catch (error) {
    if (onError) onError(error);
    else console.error('Error in streamChat:', error);
  }
};

export const clearChat = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/clear`, {
      method: 'POST',
    });
    return await response.json();
  } catch (error) {
    console.error('Error in clearChat:', error);
    throw error;
  }
};
