import React, { useEffect, useRef } from 'react';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import useChat from '../../hooks/useChat';
import { FiWifi, FiWifiOff, FiAlertCircle } from 'react-icons/fi';
import { BsChatSquareText } from 'react-icons/bs';
import '../../styles/chats/ChatScreen.css';

const ChatScreen = ({ chat }) => {
  const { messages, sendMessage, sendFile, isConnected, isLoading, error } = chat;
  const messagesEndRef = useRef(null);

  console.log('Connection check inside ChatScreen: ', isConnected);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="ds-chat-container">
      {error && (
        <div className="ds-error-banner">
          <FiAlertCircle className="ds-error-icon" />
          <span>{error}</span>
        </div>
      )}

      <div className="ds-messages-wrapper">
        <div className="ds-messages-container">
          {messages.length === 0 ? (
            <div className="ds-empty-state">
              <BsChatSquareText className="ds-empty-icon" />
              <p>How can I help you today?</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage
                key={`msg-${index}`}
                message={message}
                isCustomer={message.sender === 'user'}
              />
            ))
          )}
          <div ref={messagesEndRef} className="ds-scroll-anchor" />
        </div>
      </div>

      <div className="ds-chat-input-container">
        <ChatInput
          onSendMessage={sendMessage}
          onSendFile={sendFile}
          disabled={!isConnected || isLoading}
        />
      </div>
    </div>
  );
};

export default ChatScreen;
