import { useState, useEffect, useRef, useCallback } from 'react';
import webSocketService from '../services/websocket';
import { startCallApi, endCallApi, sendAudioApi, sendDTMFApi } from '../services/api';
import { API_URL, LOCAL_API_URL } from '../utils/constants';

const useCall = () => {
  const [callStatus, setCallStatus] = useState('idle'); // 'idle'|'connecting'|'active'|'ending'|'error'
  const [isMuted, setIsMuted] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [dtmfDigits, setDtmfDigits] = useState('');
  // const [currentAudioChunk, setCurrentAudioChunk] = useState(null);

  const audioContextRef = useRef(null);
  const audioStreamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const audioQueueRef = useRef([]);
  const activeAudioSourceRef = useRef(null);
  const callTimerRef = useRef(null);
  const audioTimeoutRef = useRef(null);
  const currentMessageIdRef = useRef(null);
  const holdMusicSourceRef = useRef(null);
  const currentRecording = useRef(null);
  const currentCallId = useRef(null);
  const currentMessageType = useRef(null);
  const isAudioPlayingRef = useRef(false);

  const callTopicRef = useRef(`/topic/call-${Date.now()}`);

  const initializeCall = useCallback(async () => {
    try {
      setCallStatus('connecting');

      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();

      audioStreamRef.current = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      initializeMediaRecord();

      const WS_URL = API_URL + "/socket";
      await webSocketService.connect(WS_URL);

      const { callId } = await startCallApi();
      currentCallId.current = callId;
      callTopicRef.current = `/topic/call-${callId}`;

      console.log('callId: ', callId);

      webSocketService.subscribe(callTopicRef.current, handleWebSocketMessage);

      startCallTimer();

      setCallStatus('active');
    } catch (error) {
      console.error('Call initialization failed:', error);
      setCallStatus('error');
      cleanupCallResources();
    }
  }, []);

  const handleWebSocketMessage = useCallback((message) => {
    switch (message.type) {
      case 'audio':
        handleIncomingAudio(message);
        break;
      case 'dtmf-request':
        handleDtmfRequest(message);
        break;
      case 'call-end':
        endCall();
        break;
      default:
        console.warn('Unknown message type:', message.type);
    }
  }, []);

  const handleIncomingAudio = useCallback((message) => {
    // If this is a new audio message, clear previous chunks
    if (message.messageId !== currentMessageIdRef.current) {
      audioQueueRef.current = [];
      currentMessageIdRef.current = message.messageId;
    }

    audioQueueRef.current.push(message.content);

    if (audioTimeoutRef.current) {
      clearTimeout(audioTimeoutRef.current);
    }

    currentMessageType.current = message.requestMessageType;
    processAudioQueue();
  }, []);

  // Handle DTMF requests
  const handleDtmfRequest = useCallback((message) => {
    // Customer should press digits which will be handled by sendDTMF

    // If this is a new audio message, clear previous chunks
    if (message.messageId !== currentMessageIdRef.current) {
      audioQueueRef.current = [];
      currentMessageIdRef.current = message.messageId;
    }

    audioQueueRef.current.push(message.content);

    if (audioTimeoutRef.current) {
      clearTimeout(audioTimeoutRef.current);
    }

    // audioTimeoutRef.current = setTimeout(() => {
    //   if (message.requestMessageType === 'audio') {
    //     playBeepSound();
    //     startCustomerRecording();
    //   } else if (message.requestMessageType === 'dtmf-request') {
    //     playBeepSound();
    //   }
    // }, 10000);

    currentMessageType.current = message.requestMessageType;
    processAudioQueue();
  }, []);

  const base64ToArrayBuffer = (base64) => {
    const binary = atob(base64);
    const len = binary.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  };

  const processAudioQueue = useCallback(async () => {
    if (audioQueueRef.current.length === 0 || !audioContextRef.current || isAudioPlayingRef.current)
      return;

    stopHoldMusic();

    try {
      isAudioPlayingRef.current = true;
      // Stop any currently playing audio
      //   if (activeAudioSourceRef.current) {
      //     activeAudioSourceRef.current.stop();
      //   }

      const audioData = audioQueueRef.current.shift();
      // setCurrentAudioChunk(audioData);
      const arrayBuffer = base64ToArrayBuffer(audioData);
      const buffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      // setCurrentAudioChunk(buffer);
      const source = audioContextRef.current.createBufferSource();
      source.buffer = buffer;
      source.connect(audioContextRef.current.destination);
      source.start();

      activeAudioSourceRef.current = source;

      source.onended = () => {
        isAudioPlayingRef.current = false;
        if (audioQueueRef.current.length > 0) {
          processAudioQueue();
        } else {
          audioTimeoutRef.current = setTimeout(() => {
            if (currentMessageType.current === 'audio') {
              playBeepSound();
              startCustomerRecording();
            } else if (currentMessageType.current === 'dtmf-request') {
              console.log('dtmf', "request");
              // playBeepSound();
            }
          }, 5000);
        }
      };
    } catch (error) {
      console.error('Audio playback error:', error);
      isAudioPlayingRef.current = false;
    }
  }, []);

  // Play beep sound before recording
  const playBeepSound = useCallback(() => {
    if (!audioContextRef.current) return;

    const oscillator = audioContextRef.current.createOscillator();
    const gainNode = audioContextRef.current.createGain();

    oscillator.type = 'sine';
    oscillator.frequency.value = 800;
    gainNode.gain.value = 0.5;

    oscillator.connect(gainNode);
    gainNode.connect(audioContextRef.current.destination);

    oscillator.start();
    oscillator.stop(audioContextRef.current.currentTime + 0.5);
  }, []);


  const startCustomerRecording = useCallback(() => {
    if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'recording') {
      console.log('Recording: ', 'discarded');
      return;
    }

    recordedChunksRef.current = [];
    mediaRecorderRef.current.start(100);
    currentRecording.current = true;
    console.log('Recording: ', 'started');
    setTimeout(() => {
      if (
        mediaRecorderRef.current &&
        mediaRecorderRef.current.state === 'recording' &&
        currentRecording.current
      ) {
        console.log('Recording: ', 'send');
        stopAndSendRecording();
        currentRecording.current = false;
      } else {
        console.log('Recording: ', 'not send');
      }
    }, 60000);
  }, []);

  // Play hold music
  // const playHoldMusic = useCallback(() => {
  //   if (!audioContextRef.current) return;

  //   // Create oscillator for simple hold music
  //   const oscillator = audioContextRef.current.createOscillator();
  //   const gainNode = audioContextRef.current.createGain();

  //   oscillator.type = 'sine';
  //   oscillator.frequency.value = 440; // A4 note
  //   gainNode.gain.value = 0.1; // Low volume

  //   oscillator.connect(gainNode);
  //   gainNode.connect(audioContextRef.current.destination);

  //   oscillator.start();
  //   holdMusicSourceRef.current = { oscillator, gainNode };
  // }, []);

  // // Stop hold music
  // const stopHoldMusic = useCallback(() => {
  //   if (holdMusicSourceRef.current) {
  //     holdMusicSourceRef.current.oscillator.stop();
  //     holdMusicSourceRef.current.gainNode.disconnect();
  //     holdMusicSourceRef.current = null;
  //   }
  // }, []);

  const playHoldMusic = useCallback(() => {
    if (!audioContextRef.current) return;

    const audioContext = audioContextRef.current;
    const audioElement = new Audio('/hold_music.mp3');
    audioElement.loop = true;
    audioElement.crossOrigin = "anonymous";

    const track = audioContext.createMediaElementSource(audioElement);
    track.connect(audioContext.destination);

    audioElement.play();

    holdMusicSourceRef.current = { audioElement, track };
  }, []);

  const stopHoldMusic = useCallback(() => {
    if (holdMusicSourceRef.current?.audioElement) {
      holdMusicSourceRef.current.audioElement.pause();
      holdMusicSourceRef.current.audioElement.currentTime = 0;
      holdMusicSourceRef.current.track.disconnect();
    }
  }, []);

  const stopAndSendRecording = useCallback(async () => {
    if (!mediaRecorderRef.current || mediaRecorderRef.current.state !== 'recording') {
      console.log('Recording: ', 'send recording discared');
      return;
    }

    return new Promise((resolve) => {
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(recordedChunksRef.current, { type: 'audio/webm' });
        const timestamp = Date.now();
        console.log('Recording: ', 'sending recording');
        currentMessageIdRef.current = timestamp.toString();
        await sendAudioApi(audioBlob, currentMessageIdRef.current, currentCallId.current);
        resolve();
      };

      currentRecording.current = false;
      mediaRecorderRef.current.stop();
    });
  }, []);

  const startCallTimer = useCallback(() => {
    let seconds = 0;
    callTimerRef.current = setInterval(() => {
      seconds++;
      setCallDuration(seconds);
    }, 1000);
  }, []);

  const cleanupCallResources = useCallback(() => {
    if (callTimerRef.current) clearInterval(callTimerRef.current);
    if (audioTimeoutRef.current) clearTimeout(audioTimeoutRef.current);

    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
    }

    if (activeAudioSourceRef.current) {
      activeAudioSourceRef.current.stop();
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
    }

    webSocketService.unsubscribe(callTopicRef.current);
  }, []);

  const endCall = useCallback(async () => {
    try {
      setCallStatus('ending');

      await stopAndSendRecording();
      await endCallApi(currentCallId.current);

      cleanupCallResources();
      setCallStatus('ended');

      setTimeout(() => {
        setCallStatus('idle');
        setCallDuration(0);
        setDtmfDigits('');
      }, 2000);
    } catch (error) {
      console.error('Error ending call:', error);
      setCallStatus('error');
    }
  }, [stopAndSendRecording, cleanupCallResources]);

  useEffect(() => {
    if (!audioStreamRef.current) {
      console.log('MediaRecordRef', 'Initialize Discard');
      return;
    }
    initializeMediaRecord();
  }, []);

  const initializeMediaRecord = useCallback(() => {
    console.log('MediaRecordRef', 'Initialize');
    mediaRecorderRef.current = new MediaRecorder(audioStreamRef.current);
    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
      }
    };

    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const sendDTMF = useCallback(
    async (digit) => {
      try {
        setDtmfDigits(prev => prev + digit);
        if (
          digit === '#' && mediaRecorderRef.current &&
          mediaRecorderRef.current.state === 'recording' &&
          currentRecording.current
        ) {
          stopAndSendRecording();
          playHoldMusic();
        } else {
          // setDtmfDigits(digit);

          const timestamp = Date.now();
          currentMessageIdRef.current = timestamp.toString();
          // Send DTMF to server
          playHoldMusic();
          await sendDTMFApi(digit, currentMessageIdRef.current, currentCallId.current);
        }

        // If # is pressed, end the call
      } catch (error) {
        console.error('Error sending DTMF:', error);
      }
    },
    [endCall],
  );

  const toggleMute = useCallback(() => {
    if (audioStreamRef.current) {
      const audioTracks = audioStreamRef.current.getAudioTracks();
      audioTracks.forEach((track) => {
        track.enabled = !track.enabled;
      });
      setIsMuted(!isMuted);
    }
  }, [isMuted]);

  return {
    callStatus,
    startCall: initializeCall,
    endCall,
    toggleMute,
    isMuted,
    sendDTMF,
    callDuration,
    dtmfDigits,
  };
};

export default useCall;
