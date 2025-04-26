class WebSocketService {
  constructor() {
    this.socket = null;
    this.subscribers = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
  }

  connect = (url) => {
    return new Promise((resolve, reject) => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        this.reconnectAttempts = 0;
        console.log('WebSocket connected');
        resolve();
      };

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleIncomingMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket disconnected:', event);
        this.handleReconnect(url);
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };
    });
  };

  handleIncomingMessage = (message) => {
    if (message.topic && this.subscribers[message.topic]) {
      this.subscribers[message.topic].forEach((callback) => {
        callback(message.payload);
      });
    } else if (!message.topic) {
      console.warn('Received message without topic:', message);
    }
  };

  handleReconnect = (url) => {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`,
      );
      setTimeout(() => this.connect(url), this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
    }
  };

  disconnect = () => {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.subscribers = {};
    }
  };

  subscribe = (topic, callback) => {
    if (!this.subscribers[topic]) {
      this.subscribers[topic] = [];
    }
    this.subscribers[topic].push(callback);

    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(
        JSON.stringify({
          action: 'subscribe',
          topic,
        }),
      );
    } else {
      console.error('WebSocket is not subscribed');
    }

    return () => {
      this.unsubscribe(topic, callback);
    };
  };

  unsubscribe = (topic, callback) => {
    if (this.subscribers[topic]) {
      this.subscribers[topic] = this.subscribers[topic].filter((cb) => cb !== callback);

      if (this.subscribers[topic].length === 0) {
        delete this.subscribers[topic];
      }
    }
  };

  publish = (topic, payload) => {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(
        JSON.stringify({
          topic,
          payload,
          timestamp: new Date().toISOString(),
        }),
      );
    } else {
      console.error('WebSocket is not connected');
    }
  };
}

const webSocketService = new WebSocketService();

export default webSocketService;
