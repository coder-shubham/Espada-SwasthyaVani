import { useState, useEffect, useCallback } from 'react';
import webSocketService from '../services/websocket';
import { sendMessageApi, uploadFileApi } from '../services/api';

const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const userDestination = `/topic/chat`;
  const broadcastTopic = `/topic/chat`;

  useEffect(() => {
    let unsubscribeUser = () => { };
    let unsubscribeBroadcast = () => { };

    const initChat = async () => {
      try {
        setIsLoading(true);
        setError(null);

        await webSocketService.connect('http://localhost:8080/socket');

        unsubscribeUser = webSocketService.subscribe(
          userDestination,
          (message) => {
            setMessages(prev => [...prev, {
              text: message.content,
              sender: message.sender,
              timestamp: message.timestamp,
              type: 'text'
            }]);
          }
        );

        // Subscribe to broadcast topic
        // unsubscribeBroadcast = webSocketService.subscribe(
        //   broadcastTopic,
        //   (message) => {
        //     if (message.type === 'SYSTEM') {
        //       setMessages(prev => [...prev, {
        //         text: message.content,
        //         sender: 'system',
        //         timestamp: message.timestamp,
        //         type: 'system'
        //       }]);
        //     }
        //   }
        // );

        setIsConnected(true);
      } catch (err) {
        console.error('Chat initialization error:', err);
        setError('Failed to connect to chat service');
        setIsConnected(false);
      } finally {
        setIsLoading(false);
      }
    };

    initChat();

    return () => {
      unsubscribeUser();
      unsubscribeBroadcast();
      webSocketService.disconnect();
    };
  }, []);

  const sendMessage = useCallback(async (message) => {
    try {
      const userMessage = {
        text: message,
        sender: 'user',
        timestamp: new Date().toISOString(),
        type: 'text'
      };
      setMessages(prev => [...prev, userMessage]);

      await sendMessageApi({
        content: message,
        type: 'USER_MESSAGE'
      });

    } catch (err) {
      console.error('Error sending message:', err);
      setMessages(prev => prev.filter(msg => msg.text !== message));
      setError('Failed to send message');

      setMessages(prev => [...prev, {
        text: 'Failed to send message',
        sender: 'system',
        timestamp: new Date().toISOString(),
        type: 'error'
      }]);
    }
  }, []);

  const sendFile = useCallback(async (file) => {
    try {
      setMessages(prev => [...prev, {
        text: `Uploading ${file.name}...`,
        sender: 'user',
        timestamp: new Date().toISOString(),
        type: 'text'
      }]);

      const response = await uploadFileApi(file);

      setMessages(prev => [...prev, {
        text: file.name,
        sender: 'user',
        timestamp: new Date().toISOString(),
        type: 'file',
        url: response.fileUrl,
        metadata: response.metadata
      }]);

      webSocketService.sendMessage('/app/chat/file', {
        fileName: file.name,
        fileUrl: response.fileUrl,
        sender: 'user',
        timestamp: new Date().toISOString()
      });

    } catch (err) {
      console.error('Error uploading file:', err);
      setError('Failed to upload file');

      setMessages(prev => [...prev, {
        text: `Failed to upload ${file.name}`,
        sender: 'system',
        timestamp: new Date().toISOString(),
        type: 'error'
      }]);
    }
  }, []);

  const endChat = useCallback(() => {
    webSocketService.sendMessage('/app/chat/end', {
      timestamp: new Date().toISOString()
    });
    webSocketService.disconnect();
    setIsConnected(false);
  }, []);

  return {
    messages,
    sendMessage,
    sendFile,
    endChat,
    isConnected,
    isLoading,
    error
  };
};

export default useChat;


