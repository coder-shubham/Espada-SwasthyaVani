import React from 'react';
import "../../styles/generic/NavBar.css";
import DropdownSwitcher from './DropdownSwitcher';

const Navbar = ({ activeTab, setActiveTab, setCallActive }) => {
  return (
    <header className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <img src="/logo.svg" alt="SwasthyaVani Logo" className="navbar-logo" />
          <h1 className="navbar-title">SwasthyaVani</h1>
        </div>
        <div className="navbar-actions">
          <DropdownSwitcher
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            setCallActive={setCallActive}
          />
        </div>
      </div>
    </header>
  );
};

export default Navbar;
