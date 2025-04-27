import React from 'react';
import { FaUser, FaRobot } from 'react-icons/fa';
import '../../styles/chats/ChatMessage.css';

const ChatMessage = ({ message, isCustomer }) => {
  const getMessageContent = () => {
    switch (message.type) {
      case 'file':
        return (
          <a href={message.url} target="_blank" rel="noopener noreferrer" className="message-file">
            <span className="file-icon">📎</span> {message.text}
          </a>
        );
      case 'error':
        return (
          <div className="error-content">
            <span className="error-icon">⚠️</span>
            {message.text}
          </div>
        );
      default:
        // Handle message text with new lines
        const formattedMessage = message.text.replace(/\n/g, '<br/>');
        return <span dangerouslySetInnerHTML={{ __html: formattedMessage }} />;
    }
  };

  return (
    <div className={`message-wrapper ${isCustomer ? 'customer' : 'agent'}`}>
      <div className="message-avatar">
        {isCustomer ? <FaUser className="user-icon" /> : <FaRobot className="agent-icon" />}
      </div>
      <div className="message-content-wrapper">
        <div className="message-sender">{isCustomer ? 'You' : 'Support Agent'}</div>
        <div className={`message-content ${message.type}`}>{getMessageContent()}</div>
        <div className="message-timestamp">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
