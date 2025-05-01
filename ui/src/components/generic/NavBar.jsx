import React from 'react';
import { FiMenu } from 'react-icons/fi';
import DropdownSwitcher from './DropdownSwitcher';
import '../../styles/generic/NavBar.css';
import { FiWifi, FiWifiOff } from 'react-icons/fi';

const Navbar = ({ activeTab, setActiveTab, setCallActive, chat }) => {
  const { isConnected } = chat;

  return (
    <header className="sv-navbar">
      <div className="sv-navbar-container">
        <div className="sv-navbar-brand">
          <img src="/logo.svg" alt="SwasthyaVani Logo" className="sv-navbar-logo" />
          <h1 className="sv-navbar-title">SwasthyaVani</h1>
        </div>

        <div className="sv-navbar-right">
          <div className="sv-dropdown-container">
            <DropdownSwitcher
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              setCallActive={setCallActive}
            />
          </div>

          <div className={`sv-connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            <div className="sv-status-indicator">
              {isConnected ? (
                <FiWifi className="sv-status-icon" />
              ) : (
                <FiWifiOff className="sv-status-icon" />
              )}
            </div>
            <span className="sv-status-text">
              {isConnected ? 'Connected' : 'Connecting...'}
            </span>
          </div>

          <button className="sv-navbar-menu">
            <FiMenu className="sv-menu-icon" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
