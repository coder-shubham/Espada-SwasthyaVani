const API_BASE = 'http://164.52.194.203:8090';
const CALL_API_BASE = 'http://164.52.194.203:8090/api/calls';

export const sendMessageApi = async (message) => {
  const response = await fetch(`${API_BASE}/api/chat/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(message),
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

export const startChatApi = async () => {
  const response = await fetch(`${API_BASE}/api/chat/start`, {
    method: 'POST',
  });
  return await response.json();
};

export const sendAudioApi = async (audioBlob, messageId, callId) => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  formData.append('messageId', messageId);
  formData.append('callId', callId);

  const response = await fetch(`${CALL_API_BASE}/audio`, {
    method: 'POST',
    body: formData,
  });
  return await response.json();
};

export const endCallApi = async (callId) => {

  const body = {
    callId,
  };

  const response = await fetch(`${CALL_API_BASE}/end`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  return await response.json();
};

export const sendDTMFApi = async (digit, messageId, callId) => {

  const body = {
    digit,
    messageId,
    callId,
  };

  const response = await fetch(`${CALL_API_BASE}/dtmf`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
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
