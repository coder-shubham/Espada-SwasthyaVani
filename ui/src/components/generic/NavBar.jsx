import React from 'react';
import { FiMenu } from 'react-icons/fi';
import DropdownSwitcher from './DropdownSwitcher';
import "../../styles/generic/NavBar.css";

const Navbar = ({ activeTab, setActiveTab, setCallActive }) => {
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
      </div>
    </header>
  );
};

export default Navbar;
