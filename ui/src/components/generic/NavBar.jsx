import React from 'react';
import "../../styles/generic/NavBar.css";
import DropdownSwitcher from './DropdownSwitcher';

const Navbar = ({ activeTab, setActiveTab, setCallActive }) => {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <img src="/logo.svg" alt="SwasthyaVani Logo" className="navbar-logo" />
        <span className="navbar-title">SwasthyaVani</span>
      </div>
      <div className="navbar-right">
        <DropdownSwitcher
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          setCallActive={setCallActive}
        />
      </div>
    </nav>
  );
};

export default Navbar;

