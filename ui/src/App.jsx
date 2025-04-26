import React, { useState } from 'react';
import './styles/global.css';
import ChatScreen from './components/chat/ChatScreen';
import CallScreen from './components/call/CallScreen';
import Navbar from './components/generic/NavBar';

const App = () => {
  const [activeTab, setActiveTab] = useState('sms');
  const [callActive, setCallActive] = useState(false);

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} setCallActive={setCallActive} />

      <main className="app-main">
        {activeTab === 'sms' ? (
          <ChatScreen />
        ) : (
          <CallScreen callActive={callActive} setCallActive={setCallActive} />
        )}
      </main>
    </div>
  );
};

export default App;
