import React, { useState } from 'react';

interface EmotionData {
  emotions: {
    [key: string]: {
      intensities: {
        [key: string]: string[];
      };
    };
  };
}

interface SelectedEmotion {
  base: string;
  intensity: string;
  sub: string;
}

interface EmotionWheelProps {
  emotions: EmotionData | null;
  onEmotionSelected: (emotion: SelectedEmotion | null) => void;
}

export const EmotionWheel: React.FC<EmotionWheelProps> = ({ emotions, onEmotionSelected }) => {
  const [selectedBase, setSelectedBase] = useState<string | null>(null);
  const [selectedIntensity, setSelectedIntensity] = useState<string | null>(null);
  const [selectedSub, setSelectedSub] = useState<string | null>(null);

  if (!emotions) {
    return (
      <div className="text-gray-500 text-center py-8">
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

  const emotionColors: { [key: string]: string } = {
    angry: 'bg-red-900/30 hover:bg-red-800/40 border-red-700',
    happy: 'bg-yellow-900/30 hover:bg-yellow-800/40 border-yellow-700',
    sad: 'bg-blue-900/30 hover:bg-blue-800/40 border-blue-700',
    fear: 'bg-purple-900/30 hover:bg-purple-800/40 border-purple-700',
    disgust: 'bg-green-900/30 hover:bg-green-800/40 border-green-700',
    surprise: 'bg-pink-900/30 hover:bg-pink-800/40 border-pink-700',
    neutral: 'bg-gray-900/30 hover:bg-gray-800/40 border-gray-700'
  };

  const getIntensities = () => {
    if (!selectedBase) return [];
    return Object.keys(emotions.emotions[selectedBase].intensities);
  };

  const getSubEmotions = () => {
    if (!selectedBase || !selectedIntensity) return [];
    return emotions.emotions[selectedBase].intensities[selectedIntensity] || [];
  };

  return (
    <div className="space-y-4">
      {selectedBase && selectedIntensity && selectedSub && (
        <div className="bg-indigo-900/20 border border-indigo-700 rounded-lg p-4 flex justify-between items-center">
          <div>
            <div className="text-sm text-gray-400">Selected Emotion:</div>
            <div className="text-lg font-medium">
              {selectedBase} → {selectedIntensity} → {selectedSub}
            </div>
          </div>
          <button
            onClick={resetSelection}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
          >
            Clear
          </button>
        </div>
      )}

      <div>
        <h3 className="text-sm font-medium mb-2 text-gray-400">
          {selectedBase ? '1. Base Emotion (selected)' : '1. Select Base Emotion'}
        </h3>
        <div className="grid grid-cols-4 gap-2">
          {baseEmotions.map(base => (
            <button
              key={base}
              onClick={() => handleBaseClick(base)}
              className={`
                p-3 rounded-lg border-2 transition-all capitalize
                ${selectedBase === base ? 'ring-2 ring-indigo-500' : ''}
                ${emotionColors[base] || 'bg-gray-800 hover:bg-gray-700 border-gray-600'}
              `}
            >
              {base}
            </button>
          ))}
        </div>
      </div>

      {selectedBase && (
        <div className="animate-fadeIn">
          <h3 className="text-sm font-medium mb-2 text-gray-400">
            {selectedIntensity ? '2. Intensity Level (selected)' : '2. Select Intensity Level'}
          </h3>
          <div className="grid grid-cols-3 gap-2">
            {getIntensities().map(intensity => (
              <button
                key={intensity}
                onClick={() => handleIntensityClick(intensity)}
                className={`
                  p-3 rounded-lg border-2 transition-all capitalize
                  ${selectedIntensity === intensity ? 'ring-2 ring-indigo-500' : ''}
                  ${emotionColors[selectedBase]}
                `}
              >
                {intensity}
              </button>
            ))}
          </div>
        </div>
      )}

      {selectedBase && selectedIntensity && (
        <div className="animate-fadeIn">
          <h3 className="text-sm font-medium mb-2 text-gray-400">
            {selectedSub ? '3. Specific Emotion (selected)' : '3. Select Specific Emotion'}
          </h3>
          <div className="grid grid-cols-3 gap-2">
            {getSubEmotions().map(sub => (
              <button
                key={sub}
                onClick={() => handleSubClick(sub)}
                className={`
                  p-3 rounded-lg border-2 transition-all capitalize
                  ${selectedSub === sub ? 'ring-2 ring-indigo-500' : ''}
                  ${emotionColors[selectedBase]}
                `}
              >
                {sub}
              </button>
            ))}
          </div>
        </div>
      )}

      {!selectedBase && (
        <div className="text-sm text-gray-500 italic text-center py-4">
          Choose your emotional starting point above
        </div>
      )}
    </div>
  );
};
