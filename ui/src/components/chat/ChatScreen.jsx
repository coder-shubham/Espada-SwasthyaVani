import React, { useEffect, useRef } from 'react';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import useChat from '../../hooks/useChat';
import '../../styles/chats/ChatScreen.css';

const ChatScreen = () => {
  const { messages, sendMessage, sendFile, isConnected, isLoading, error } = useChat();

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-title">Customer Support Chat</div>
        <div className="chat-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? (
              <>
                <span className="status-dot connected"></span>
                Online
              </>
            ) : (
              <>
                <span className="status-dot disconnected"></span>
                Offline
              </>
            )}
          </span>
          {isLoading && <span className="loading-indicator">Connecting...</span>}
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <p>Start chatting with our support team</p>
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
        <div ref={messagesEndRef} className="scroll-anchor" />
      </div>

      <div className="chat-input-container">
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
