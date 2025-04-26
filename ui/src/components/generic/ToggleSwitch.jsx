import React from 'react';
import '../styles/global.css';

const ToggleSwitch = ({ activeTab, setActiveTab, setCallActive }) => {
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'call') {
      setCallActive(false);
    }
  };

  return (
    <div className="toggle-container">
      <button
        className={`toggle-btn ${activeTab === 'sms' ? 'active' : ''}`}
        onClick={() => handleTabChange('sms')}
      >
        SMS
      </button>
      <button
        className={`toggle-btn ${activeTab === 'call' ? 'active' : ''}`}
        onClick={() => handleTabChange('call')}
      >
        Call
      </button>
    </div>
  );
};

export default ToggleSwitch;
