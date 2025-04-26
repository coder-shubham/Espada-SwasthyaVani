import { Client } from '@stomp/stompjs';
import SockJS from 'sockjs-client';

class WebSocketService {
  constructor() {
    this.client = null;
    this.subscriptions = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.connectionUrl = null;
  }

  connect = (url) => {
    this.connectionUrl = url;

    return new Promise((resolve, reject) => {
      if (this.client && this.client.connected) {
        resolve();
        return;
      }

      const socket = new SockJS(url);

      this.client = new Client({
        webSocketFactory: () => socket,
        reconnectDelay: this.reconnectDelay,
        heartbeatIncoming: 4000,
        heartbeatOutgoing: 4000,

        onConnect: () => {
          this.reconnectAttempts = 0;
          console.log('STOMP connected');
          resolve();
        },

        onStompError: (error) => {
          console.error('STOMP error:', error);
          reject(error);
        },

        onWebSocketClose: () => {
          console.log('STOMP connection closed');
          this.handleReconnect();
        },

        onDisconnect: () => {
          console.log('STOMP disconnected');
        }
      });

      this.client.activate();
    });
  };

  subscribe = (destination, callback) => {
    if (!this.client || !this.client.connected) {
      throw new Error('STOMP client not connected');
    }

    const subscription = this.client.subscribe(
      destination,
      (message) => {
        try {
          const parsedBody = JSON.parse(message.body);
          console.log("Received Webhook Message: ", parsedBody);
          callback(parsedBody);
        } catch (error) {
          console.error('Error parsing STOMP message:', error);
        }
      }
    );

    this.subscriptions[destination] = subscription;
    return () => this.unsubscribe(destination);
  };

  unsubscribe = (destination) => {
    if (this.subscriptions[destination]) {
      this.subscriptions[destination].unsubscribe();
      delete this.subscriptions[destination];
    }
  };

  sendMessage = (destination, body, headers = {}) => {
    if (!this.client || !this.client.connected) {
      throw new Error('STOMP client not connected');
    }

    this.client.publish({
      destination,
      body: JSON.stringify(body),
      headers
    });
  };

  disconnect = () => {
    if (this.client) {
      Object.keys(this.subscriptions).forEach(dest => {
        this.unsubscribe(dest);
      });

      this.client.deactivate();
      this.client = null;
    }
  };

  handleReconnect = () => {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout(() => this.connect(this.connectionUrl), this.reconnectDelay);
    }
  };

  isConnected = () => {
    return this.client && this.client.connected;
  };
}

const webSocketService = new WebSocketService();
export default webSocketService;
