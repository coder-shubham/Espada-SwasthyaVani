import React, { useState } from 'react';
import "../../styles/generic/DropdownSwitcher.css";

const DropdownSwitcher = ({ activeTab, setActiveTab, setCallActive }) => {
  const [open, setOpen] = useState(false);

  const handleSelect = (tab) => {
    setActiveTab(tab);
    setCallActive(tab === 'call' ? false : null);
    setOpen(false);
  };

  return (
    <div className="dropdown-switcher">
      <button className="dropdown-button" onClick={() => setOpen(!open)}>
        {activeTab === 'sms' ? 'SMS' : 'Call'}
        <span className="arrow">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="dropdown-menu">
          <div className="dropdown-item" onClick={() => handleSelect('sms')}>
            SMS
          </div>
          <div className="dropdown-item" onClick={() => handleSelect('call')}>
            Call
          </div>
        </div>
      )}
    </div>
  );
};

export default DropdownSwitcher;

