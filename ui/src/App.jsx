import React, { useState } from 'react';
import './styles/global.css';
import ChatScreen from './components/chat/ChatScreen';
import CallScreen from './components/call/CallScreen';
import ToggleSwitch from './components/generic/ToggleSwitch';

const App = () => {
  const [activeTab, setActiveTab] = useState('sms');
  const [callActive, setCallActive] = useState(false);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Swasthyavani Portal</h1>
        <ToggleSwitch
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          setCallActive={setCallActive}
        />
      </header>

      <main className="app-main">
        {activeTab === 'sms' ? (
          <ChatScreen />
        ) : (
          < CallScreen
            callActive={callActive}
            setCallActive={setCallActive}
          />
        )}
      </main>
    </div>
  );
};

export default App;
