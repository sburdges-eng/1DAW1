import React, { useState } from 'react';

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
      <div style={{ 
        textAlign: 'center', 
        padding: '20px', 
        color: '#666',
        fontStyle: 'italic'
      }}>
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

  const getIntensities = () => {
    if (!selectedBase) return [];
    return Object.keys(emotions.emotions[selectedBase].intensities);
  };

  const getSubEmotions = () => {
    if (!selectedBase || !selectedIntensity) return [];
    return emotions.emotions[selectedBase].intensities[selectedIntensity] || [];
  };

  const selectedEmotion = selectedBase && selectedIntensity && selectedSub
    ? { base: selectedBase, intensity: selectedIntensity, sub: selectedSub }
    : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {selectedEmotion && (
        <div className="animate-fadeIn" style={{
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          border: '1px solid #6366f1',
          borderRadius: '8px',
          padding: '15px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ fontSize: '0.875rem', color: '#999', marginBottom: '5px' }}>
              Selected Emotion:
            </div>
            <div style={{ fontSize: '1.125rem', fontWeight: '500' }}>
              {selectedEmotion.base} → {selectedEmotion.intensity} → {selectedEmotion.sub}
            </div>
          </div>
          <button
            onClick={resetSelection}
            style={{
              padding: '6px 12px',
              backgroundColor: '#4b5563',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#374151'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#4b5563'}
          >
            Clear
          </button>
        </div>
      )}

      <div>
        <h4 style={{ 
          fontSize: '0.875rem', 
          fontWeight: '500', 
          marginBottom: '10px',
          color: '#666'
        }}>
          {selectedBase ? '1. Base Emotion (selected)' : '1. Select Base Emotion'}
        </h4>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '8px'
        }}>
          {baseEmotions.map(base => {
            const colors = getEmotionColor(base);
            const isSelected = selectedBase === base;
            return (
              <button
                key={base}
                onClick={() => handleBaseClick(base)}
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  border: `2px solid ${isSelected ? '#6366f1' : colors.border}`,
                  backgroundColor: isSelected ? colors.hover : colors.bg,
                  cursor: 'pointer',
                  textTransform: 'capitalize',
                  transition: 'all 0.2s',
                  outline: isSelected ? '2px solid rgba(99, 102, 241, 0.3)' : 'none',
                  outlineOffset: '2px'
                }}
                onMouseOver={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = colors.hover;
                  }
                }}
                onMouseOut={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = colors.bg;
                  }
                }}
              >
                {base}
              </button>
            );
          })}
        </div>
      </div>

      {selectedBase && (
        <div className="animate-fadeIn">
          <h4 style={{ 
            fontSize: '0.875rem', 
            fontWeight: '500', 
            marginBottom: '10px',
            color: '#666'
          }}>
            {selectedIntensity ? '2. Intensity Level (selected)' : '2. Select Intensity Level'}
          </h4>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '8px'
          }}>
            {getIntensities().map(intensity => {
              const colors = getEmotionColor(selectedBase);
              const isSelected = selectedIntensity === intensity;
              return (
                <button
                  key={intensity}
                  onClick={() => handleIntensityClick(intensity)}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    border: `2px solid ${isSelected ? '#6366f1' : colors.border}`,
                    backgroundColor: isSelected ? colors.hover : colors.bg,
                    cursor: 'pointer',
                    textTransform: 'capitalize',
                    transition: 'all 0.2s',
                    outline: isSelected ? '2px solid rgba(99, 102, 241, 0.3)' : 'none',
                    outlineOffset: '2px'
                  }}
                  onMouseOver={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.backgroundColor = colors.hover;
                    }
                  }}
                  onMouseOut={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.backgroundColor = colors.bg;
                    }
                  }}
                >
                  {intensity}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {selectedBase && selectedIntensity && (
        <div className="animate-fadeIn">
          <h4 style={{ 
            fontSize: '0.875rem', 
            fontWeight: '500', 
            marginBottom: '10px',
            color: '#666'
          }}>
            {selectedSub ? '3. Specific Emotion (selected)' : '3. Select Specific Emotion'}
          </h4>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '8px'
          }}>
            {getSubEmotions().map(sub => {
              const colors = getEmotionColor(selectedBase);
              const isSelected = selectedSub === sub;
              return (
                <button
                  key={sub}
                  onClick={() => handleSubClick(sub)}
                  style={{
                    padding: '12px',
                    borderRadius: '8px',
                    border: `2px solid ${isSelected ? '#6366f1' : colors.border}`,
                    backgroundColor: isSelected ? colors.hover : colors.bg,
                    cursor: 'pointer',
                    textTransform: 'capitalize',
                    transition: 'all 0.2s',
                    outline: isSelected ? '2px solid rgba(99, 102, 241, 0.3)' : 'none',
                    outlineOffset: '2px'
                  }}
                  onMouseOver={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.backgroundColor = colors.hover;
                    }
                  }}
                  onMouseOut={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.backgroundColor = colors.bg;
                    }
                  }}
                >
                  {sub}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {!selectedBase && (
        <div style={{
          fontSize: '0.875rem',
          color: '#666',
          fontStyle: 'italic',
          textAlign: 'center',
          padding: '20px 0'
        }}>
          Choose your emotional starting point above
        </div>
      )}
    </div>
  );
};
