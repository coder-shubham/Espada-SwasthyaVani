import React from 'react';
import CallControls from './CallControls';
import Keypad from './Keypad';
import AudioVisualizer from './AudioVisualizer';
import useCall from '../../hooks/useCall';
import '../../styles/call/CallScreen.css';

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
    currentAudioChunk,
  } = useCall();

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
      .toString()
      .padStart(2, '0');
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
            <div className="call-timer">{formatDuration(callDuration)}</div>
          </div>

          {/* <div className="audio-visualizer-container"> */}
          {/*   <AudioVisualizer audioChunk={currentAudioChunk} /> */}
          {/* </div> */}

          <div className="dtmf-display">
            {dtmfDigits || <span className="dtmf-placeholder">Enter digits...</span>}
          </div>

          <div className="call-controls">
            <CallControls
              isMuted={isMuted}
              toggleMute={toggleMute}
              endCall={endCall}
            />
          </div>

          <div className="keypad-container">
            <Keypad onKeyPress={sendDTMF} />
          </div>
        </div>
      )}
    </div>
  );
};

export default CallScreen;
