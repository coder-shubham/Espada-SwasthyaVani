import React from 'react';
import { FiMenu } from 'react-icons/fi';
import DropdownSwitcher from './DropdownSwitcher';
import '../../styles/generic/NavBar.css';
import { FiWifi, FiWifiOff, FiAlertCircle } from 'react-icons/fi';
import '../../styles/chats/ChatScreen.css';

const Navbar = ({ activeTab, setActiveTab, setCallActive, chat }) => {
  const { isConnected } = chat;

  return (
    <header className="ds-navbar">
      <div className="ds-navbar-container">
        <div className="ds-navbar-brand">
          <img src="/logo.svg" alt="SwasthyaVani Logo" className="ds-navbar-logo" />
          <h1 className="ds-navbar-title">SwasthyaVani</h1>
        </div>
        <div className="ds-navbar-actions">
          <DropdownSwitcher
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            setCallActive={setCallActive}
          />
          <button className="ds-navbar-menu">
            <FiMenu className="ds-menu-icon" />
          </button>
        </div>
        <div className="ds-chat-status">
          <span
            className={`ds-status-indicator ${isConnected ? 'ds-connected' : 'ds-disconnected'}`}
          >
            {isConnected ? (
              <>
                <FiWifi className="ds-status-icon" />
                <span>Connected</span>
              </>
            ) : (
              <>
                <FiWifiOff className="ds-status-icon" />
                <span>Connecting...</span>
              </>
            )}
          </span>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
