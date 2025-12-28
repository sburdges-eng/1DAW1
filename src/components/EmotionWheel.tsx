import React, { useState } from 'react';
import './EmotionWheel.css';

export interface SelectedEmotion {
  base: string;
  intensity: string;
  sub: string;
}

interface EmotionData {
  emotions: {
    [key: string]: {
      intensities: {
        [key: string]: string[];
      };
    };
  };
}

export interface SelectedEmotion {
  base: string;
  intensity: string;
  sub: string;
}

interface EmotionWheelProps {
  emotions: EmotionData | null;
  onEmotionSelected: (emotion: SelectedEmotion | null) => void;
}

const getEmotionColor = (base: string): { bg: string; border: string; hover: string } => {
  const colors: { [key: string]: { bg: string; border: string; hover: string } } = {
    angry: { bg: 'rgba(220, 38, 38, 0.2)', border: '#dc2626', hover: 'rgba(220, 38, 38, 0.3)' },
    happy: { bg: 'rgba(234, 179, 8, 0.2)', border: '#eab308', hover: 'rgba(234, 179, 8, 0.3)' },
    sad: { bg: 'rgba(59, 130, 246, 0.2)', border: '#3b82f6', hover: 'rgba(59, 130, 246, 0.3)' },
    fear: { bg: 'rgba(168, 85, 247, 0.2)', border: '#a855f7', hover: 'rgba(168, 85, 247, 0.3)' },
    disgust: { bg: 'rgba(34, 197, 94, 0.2)', border: '#22c55e', hover: 'rgba(34, 197, 94, 0.3)' },
    surprise: { bg: 'rgba(236, 72, 153, 0.2)', border: '#ec4899', hover: 'rgba(236, 72, 153, 0.3)' },
    neutral: { bg: 'rgba(107, 114, 128, 0.2)', border: '#6b7280', hover: 'rgba(107, 114, 128, 0.3)' }
  };
  return colors[base] || colors.neutral;
};

export const EmotionWheel: React.FC<EmotionWheelProps> = ({ emotions, onEmotionSelected }) => {
  const [selectedBase, setSelectedBase] = useState<string | null>(null);
  const [selectedIntensity, setSelectedIntensity] = useState<string | null>(null);
  const [selectedSub, setSelectedSub] = useState<string | null>(null);

  if (!emotions) {
    return (
      <div className="emotion-wheel-empty">
        Load emotions to begin selection
      </div>
    );
  }

  const baseEmotions = Object.keys(emotions.emotions);

  const handleBaseClick = (base: string) => {
    setSelectedBase(base);
    setSelectedIntensity(null);
    setSelectedSub(null);
    onEmotionSelected(null);
  };

  const handleIntensityClick = (intensity: string) => {
    setSelectedIntensity(intensity);
    setSelectedSub(null);
    onEmotionSelected(null);
  };

  const handleSubClick = (sub: string) => {
    setSelectedSub(sub);
    if (selectedBase && selectedIntensity) {
      onEmotionSelected({
        base: selectedBase,
        intensity: selectedIntensity,
        sub: sub
      });
    }
  };

  const resetSelection = () => {
    setSelectedBase(null);
    setSelectedIntensity(null);
    setSelectedSub(null);
    onEmotionSelected(null);
  };

  const getEmotionColorClass = (emotion: string): string => {
    const emotionLower = emotion.toLowerCase();
    if (emotionLower.includes('angry') || emotionLower === 'anger') return 'emotion-angry';
    if (emotionLower.includes('sad') || emotionLower === 'sadness') return 'emotion-sad';
    if (emotionLower.includes('happy') || emotionLower === 'joy' || emotionLower === 'happiness') return 'emotion-happy';
    if (emotionLower.includes('fear') || emotionLower === 'fear') return 'emotion-fear';
    if (emotionLower.includes('disgust') || emotionLower === 'disgust') return 'emotion-disgust';
    if (emotionLower.includes('surprise') || emotionLower === 'surprise') return 'emotion-surprise';
    return 'emotion-neutral';
  };

  const getIntensities = () => {
    if (!selectedBase || !emotions?.emotions[selectedBase]) return [];
    return Object.keys(emotions.emotions[selectedBase].intensities || {});
  };

  const getSubEmotions = () => {
    if (!selectedBase || !selectedIntensity || !emotions?.emotions[selectedBase]) return [];
    return emotions.emotions[selectedBase].intensities?.[selectedIntensity] || [];
  };

  const capitalize = (str: string): string => {
    if (!str) return str;
    return str.charAt(0).toUpperCase() + str.slice(1);
  };

  const selectedEmotion = selectedBase && selectedIntensity && selectedSub
    ? { base: selectedBase, intensity: selectedIntensity, sub: selectedSub }
    : null;

  return (
    <div className="emotion-wheel-container">
      {selectedBase && selectedIntensity && selectedSub && (
        <div className="emotion-wheel-selected animate-fadeIn">
          <div className="emotion-wheel-selected-content">
            <div className="emotion-wheel-selected-label">Selected Emotion:</div>
            <div className="emotion-wheel-selected-value">
              {capitalize(selectedBase)} → {capitalize(selectedIntensity)} → {capitalize(selectedSub)}
            </div>
          </div>
          <button
            onClick={resetSelection}
            className="emotion-wheel-clear-btn"
          >
            Clear
          </button>
        </div>
      )}

      <div className="emotion-wheel-step">
        <h4 className="emotion-wheel-step-title">
          {selectedBase ? '1. Base Emotion (selected)' : '1. Select Base Emotion'}
        </h4>
        <div className="emotion-wheel-grid emotion-wheel-grid-base">
          {baseEmotions.map(base => (
            <button
              key={base}
              onClick={() => handleBaseClick(base)}
              className={`emotion-wheel-btn ${getEmotionColorClass(base)} ${selectedBase === base ? 'emotion-wheel-btn-selected' : ''}`}
            >
              {capitalize(base)}
            </button>
          ))}
        </div>
      </div>

      {selectedBase && (
        <div className="emotion-wheel-step animate-fadeIn">
          <h4 className="emotion-wheel-step-title">
            {selectedIntensity ? '2. Intensity Level (selected)' : '2. Select Intensity Level'}
          </h4>
          <div className="emotion-wheel-grid emotion-wheel-grid-intensity">
            {getIntensities().map(intensity => (
              <button
                key={intensity}
                onClick={() => handleIntensityClick(intensity)}
                className={`emotion-wheel-btn ${getEmotionColorClass(selectedBase)} ${selectedIntensity === intensity ? 'emotion-wheel-btn-selected' : ''}`}
              >
                {capitalize(intensity)}
              </button>
            ))}
          </div>
        </div>
      )}

      {selectedBase && selectedIntensity && (
        <div className="emotion-wheel-step animate-fadeIn">
          <h4 className="emotion-wheel-step-title">
            {selectedSub ? '3. Specific Emotion (selected)' : '3. Select Specific Emotion'}
          </h4>
          <div className="emotion-wheel-grid emotion-wheel-grid-sub">
            {getSubEmotions().map(sub => (
              <button
                key={sub}
                onClick={() => handleSubClick(sub)}
                className={`emotion-wheel-btn ${getEmotionColorClass(selectedBase)} ${selectedSub === sub ? 'emotion-wheel-btn-selected' : ''}`}
              >
                {capitalize(sub)}
              </button>
            ))}
          </div>
        </div>
      )}

      {!selectedBase && (
        <div className="emotion-wheel-empty">
          Choose your emotional starting point above
        </div>
      )}
    </div>
  );
};
