import React, { useState } from 'react';
import "../../styles/generic/DropdownSwitcher.css";
import { RiArrowDownSLine, RiArrowUpSLine, RiMessage2Line, RiPhoneLine } from 'react-icons/ri';

const DropdownSwitcher = ({ activeTab, setActiveTab, setCallActive }) => {
  const [open, setOpen] = useState(false);

  const handleSelect = (tab) => {
    setActiveTab(tab);
    setCallActive(tab === 'call' ? false : null);
    setOpen(false);
  };

  return (
    <div className="dropdown-switcher">
      <button
        className="dropdown-button"
        onClick={() => setOpen(!open)}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        {activeTab === 'sms' ? (
          <>
            <RiMessage2Line className="dropdown-icon" />
            <span>SMS</span>
          </>
        ) : (
          <>
            <RiPhoneLine className="dropdown-icon" />
            <span>Call</span>
          </>
        )}
        <span className="dropdown-arrow">
          {open ? <RiArrowUpSLine /> : <RiArrowDownSLine />}
        </span>
      </button>
      {open && (
        <div className="dropdown-menu" role="listbox">
          <button
            className={`dropdown-item ${activeTab === 'sms' ? 'active' : ''}`}
            onClick={() => handleSelect('sms')}
            role="option"
            aria-selected={activeTab === 'sms'}
          >
            <RiMessage2Line className="dropdown-icon" />
            <span>SMS</span>
          </button>
          <button
            className={`dropdown-item ${activeTab === 'call' ? 'active' : ''}`}
            onClick={() => handleSelect('call')}
            role="option"
            aria-selected={activeTab === 'call'}
          >
            <RiPhoneLine className="dropdown-icon" />
            <span>Call</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default DropdownSwitcher;
