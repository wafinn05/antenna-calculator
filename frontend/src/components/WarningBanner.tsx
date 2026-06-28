import React from 'react';

interface WarningBannerProps {
  warnings: string[];
}

export const WarningBanner: React.FC<WarningBannerProps> = ({ warnings }) => {
  if (warnings.length === 0) return null;

  return (
    <>
      {warnings.map((warning, index) => (
        <div key={index} className="warning-banner">
          <div className="warning-title">
            ⚠️ Model Validity Warning
          </div>
          <div className="warning-text">{warning}</div>
        </div>
      ))}
    </>
  );
};
