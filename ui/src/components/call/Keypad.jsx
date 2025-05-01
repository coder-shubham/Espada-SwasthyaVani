import React from 'react';
import '../../styles/call/Keypad.css';

const Keypad = ({ onKeyPress }) => {
  const keys = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
  ];

  return (
    <div className="keypad-container">
      <div className="keypad-grid">
        {keys.map((row, rowIndex) => (
          <div key={rowIndex} className="keypad-row">
            {row.map((key) => (
              <button
                key={key}
                className="keypad-button"
                onClick={() => onKeyPress(key)}
              >
                {key}
              </button>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Keypad;
