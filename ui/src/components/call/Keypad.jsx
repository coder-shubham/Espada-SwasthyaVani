import React from 'react';
import '../../styles/call/Keypad.css';

const Keypad = ({ onKeyPress }) => {
  const buttons = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#'],
  ];

  return (
    <div className="keypad-container">
      {buttons.map((row, rowIndex) => (
        <React.Fragment key={rowIndex}>
          {row.map((digit) => (
            <button key={digit} className="keypad-button" onClick={() => onKeyPress(digit)}>
              {digit}
            </button>
          ))}
        </React.Fragment>
      ))}
    </div>
  );
};

export default Keypad;
