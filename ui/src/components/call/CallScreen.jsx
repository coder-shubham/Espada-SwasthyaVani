import React, { useEffect } from 'react';
import CallControls from './CallControls';
import Keypad from './Keypad';
import AudioVisualizer from './AudioVisualizer';
import useCall from '../../hooks/useCall';
import './styles.css';

const CallScreen = () => {
  const {
    callStatus,
    startCall,
    endCall,
    toggleMute,
    isMuted,
    sendDTMF,
    callDuration,
    dtmfDigits,
    currentAudioChunk
  } = useCall();

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
    const secs = (seconds % 60).toString().padStart(2, '0');
    return `${mins}:${secs}`;
  };

  return (
    <div className="call-container">
      {callStatus === 'idle' ? (
        <div className="call-init-screen">
          <h2>Voice Support</h2>
          <button
            className="start-call-button"
            onClick={startCall}
            disabled={callStatus === 'connecting'}
          >
            {callStatus === 'connecting' ? 'Connecting...' : 'Start Call'}
          </button>
        </div>
      ) : (
        <div className="call-active-screen">
          <div className="call-status-bar">
            <div className={`status-indicator ${callStatus}`}>
              {callStatus.toUpperCase()}
            </div>
            <div className="call-timer">
              {formatDuration(callDuration)}
            </div>
          </div>

          <AudioVisualizer audioChunk={currentAudioChunk} />

          <div className="dtmf-display">
            {dtmfDigits || 'Enter digits...'}
          </div>

          <CallControls
            isMuted={isMuted}
            toggleMute={toggleMute}
            endCall={endCall}
          />

          <Keypad onKeyPress={sendDTMF} />
        </div>
      )}
    </div>
  );
};

export default CallScreen;


