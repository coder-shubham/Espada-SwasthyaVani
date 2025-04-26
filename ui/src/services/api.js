const API_BASE = 'http://localhost:8080';
const CALL_API_BASE = 'http://localhost:8080/api/calls';

export const sendMessageApi = async (message) => {
  const response = await fetch(`${API_BASE}/api/chat/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content: message }),
  });
  return await response.json();
};

export const uploadFileApi = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  return await response.json();
};

export const startCallApi = async () => {
  const response = await fetch(`${CALL_API_BASE}/start`, {
    method: 'POST',
  });
  return await response.json();
};

export const sendAudioApi = async (audioBlob, messageId) => {

  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  formData.append('messageId', messageId);

  const response = await fetch(`${CALL_API_BASE}/audio`, {
    method: 'POST',
    body: formData,
  });
  return await response.json();
};

export const endCallApi = async () => {
  const response = await fetch(`${API_BASE}/calls/end`, {
    method: 'POST',
  });
  return await response.json();
};

export const sendDTMFApi = async (digit) => {
  const response = await fetch(`${API_BASE}/calls/dtmf`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ digit }),
  });
  return await response.json();
};

export const uploadAudioApi = async (audioBlob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');

  const response = await fetch(`${API_BASE}/calls/upload-audio`, {
    method: 'POST',
    body: formData,
  });
  return await response.json();
};
