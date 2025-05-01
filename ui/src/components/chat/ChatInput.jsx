import React, { useState, useRef } from 'react';
import { FiPaperclip, FiSend } from 'react-icons/fi';
import '../../styles/chats/ChatInput.css';

const ChatInput = ({ onSendMessage, onSendFile, disabled }) => {
  const [message, setMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && !disabled) {
      onSendFile(file);
      e.target.value = '';
    }
  };

  return (
    <form onSubmit={handleSubmit} className="ds-chat-input-form">
      <div className="ds-input-wrapper">
        <input
          type="text"
          className="ds-chat-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={disabled}
        />

        <div className="ds-input-actions">
          <button
            type="button"
            className="ds-file-button"
            onClick={() => fileInputRef.current.click()}
            disabled={disabled}
          >
            <FiPaperclip className="ds-file-icon" />
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: 'none' }}
              disabled={disabled}
            />
          </button>

          <button type="submit" className="ds-send-button" disabled={!message.trim() || disabled}>
            <FiSend className="ds-send-icon" />
          </button>
        </div>
      </div>
    </form>
  );
};

export default ChatInput;
