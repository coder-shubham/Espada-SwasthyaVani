import React, { useEffect, useRef, useState } from 'react';
import '../../styles/call/AudioVisualizer.css';

const AudioVisualizer = ({ audioChunk }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);

  useEffect(() => {
    const initAudioContext = async () => {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContextRef.current = new AudioContext();
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;

        const bufferLength = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLength);

        setIsActive(true);
      } catch (error) {
        console.error('AudioContext initialization failed:', error);
        setIsActive(false);
      }
    };

    initAudioContext();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (!audioChunk || !audioContextRef.current || !isActive) return;

    const processAudioChunk = async () => {
      try {
        let audioData;
        if (audioChunk instanceof Blob) {
          audioData = await blobToArrayBuffer(audioChunk);
        } else if (audioChunk instanceof ArrayBuffer) {
          audioData = audioChunk;
        } else {
          console.error('Unsupported audio chunk format:', audioChunk);
          return;
        }

        const audioBuffer = await audioContextRef.current.decodeAudioData(audioData);
        const source = audioContextRef.current.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(analyserRef.current);
        analyserRef.current.connect(audioContextRef.current.destination);
        source.start();
      } catch (error) {
        console.error('Audio processing error:', error);
      }
    };

    const blobToArrayBuffer = (blob) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsArrayBuffer(blob);
      });
    };

    processAudioChunk();
  }, [audioChunk, isActive]);

  useEffect(() => {
    if (!isActive || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    const WIDTH = canvas.width;
    const HEIGHT = canvas.height;

    const draw = () => {
      animationRef.current = requestAnimationFrame(draw);

      if (!analyserRef.current || !dataArrayRef.current) return;

      analyserRef.current.getByteFrequencyData(dataArrayRef.current);

      canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);

      const barWidth = (WIDTH / dataArrayRef.current.length) * 2.5;
      let x = 0;

      for (let i = 0; i < dataArrayRef.current.length; i++) {
        const barHeight = (dataArrayRef.current[i] / 255) * HEIGHT;

        const gradient = canvasCtx.createLinearGradient(0, HEIGHT - barHeight, 0, HEIGHT);
        gradient.addColorStop(0, '#3b82f6');
        gradient.addColorStop(0.7, '#2563eb');
        gradient.addColorStop(1, '#1d4ed8');

        canvasCtx.fillStyle = gradient;
        canvasCtx.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);

        x += barWidth + 1;
      }
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive]);

  return (
    <div className="audio-visualizer">
      <canvas
        ref={canvasRef}
        width={400}
        height={120}
        className="audio-visualizer-canvas"
      />
      <div className={`audio-status ${isActive ? 'active' : ''}`}>
        <span className="audio-status-indicator"></span>
        {isActive ? 'Audio Active' : 'Audio Inactive'}
      </div>
    </div>
  );
};

export default AudioVisualizer;
