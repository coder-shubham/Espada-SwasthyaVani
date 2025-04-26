import React, { useState, useRef } from 'react';
import { FaPaperclip, FaPaperPlane } from 'react-icons/fa';
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
    <form onSubmit={handleSubmit} className="chat-input-form">
      <div className="input-wrapper">
        <input
          type="text"
          className="chat-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={disabled}
        />

        <div className="input-actions">
          <button
            type="button"
            className="file-button"
            onClick={() => fileInputRef.current.click()}
            disabled={disabled}
          >
            <FaPaperclip className="file-icon" />
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: 'none' }}
              disabled={disabled}
            />
          </button>

          <button type="submit" className="send-button" disabled={!message.trim() || disabled}>
            <FaPaperPlane className="send-icon" />
          </button>
        </div>
      </div>
    </form>
  );
};

export default ChatInput;
