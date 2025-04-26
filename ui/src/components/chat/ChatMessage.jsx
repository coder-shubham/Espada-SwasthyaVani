import React from 'react';
import { FaUser, FaRobot } from 'react-icons/fa';
import { FiPaperclip, FiAlertCircle } from 'react-icons/fi';
import { format } from 'date-fns';
import "../../styles/chats/ChatMessage.css";

const ChatMessage = ({ message, isCustomer }) => {
  const getMessageContent = () => {
    switch (message.type) {
      case 'file':
        return (
          <a
            href={message.url}
            target="_blank"
            rel="noopener noreferrer"
            className="ds-message-file"
          >
            <FiPaperclip className="ds-file-icon" />
            <span>{message.text}</span>
          </a>
        );
      case 'error':
        return (
          <div className="ds-error-content">
            <FiAlertCircle className="ds-error-icon" />
            <span>{message.text}</span>
          </div>
        );
      default:
        return message.text;
    }
  };

  return (
    <div className={`ds-message-wrapper ${isCustomer ? 'ds-customer' : 'ds-agent'}`}>
      <div className="ds-message-avatar">
        {isCustomer ? (
          <FaUser className="ds-user-icon" />
        ) : (
          <FaRobot className="ds-agent-icon" />
        )}
      </div>
      <div className="ds-message-content-wrapper">
        <div className="ds-message-sender">{isCustomer ? 'You' : 'Support'}</div>
        <div className={`ds-message-content ${message.type}`}>
          {getMessageContent()}
        </div>
        <div className="ds-message-timestamp">
          {format(new Date(message.timestamp), 'h:mm a')}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
