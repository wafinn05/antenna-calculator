import React, { useState, useCallback } from 'react';
import type {
  FrequencyUnit,
  LengthUnit,
  PatchAntennaRequest,
} from '../types';
import { MATERIAL_PRESETS } from '../types';

interface InputFormProps {
  onSubmit: (request: PatchAntennaRequest) => void;
  isLoading: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({ onSubmit, isLoading }) => {
  const [frequency, setFrequency] = useState<string>('2.4');
  const [frequencyUnit, setFrequencyUnit] = useState<FrequencyUnit>('GHz');
  const [dielectricConstant, setDielectricConstant] = useState<string>('4.4');
  const [presetKey, setPresetKey] = useState<string>('FR4');
  const [substrateHeight, setSubstrateHeight] = useState<string>('1.6');
  const [heightUnit, setHeightUnit] = useState<LengthUnit>('mm');
  const [advancedEnabled, setAdvancedEnabled] = useState(true);
  const [feedImpedance, setFeedImpedance] = useState<string>('50');
  const [useInsetFeed, setUseInsetFeed] = useState(true);

  const handlePresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const key = e.target.value;
    setPresetKey(key);
    if (key !== 'CUSTOM') {
      const preset = MATERIAL_PRESETS.find((m) => m.key === key);
      if (preset) {
        setDielectricConstant(preset.epsilon_r.toString());
      }
    }
  };

  const handleDielectricChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDielectricConstant(e.target.value);
    setPresetKey('CUSTOM');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const request: PatchAntennaRequest = {
      frequency: parseFloat(frequency) || 2.4,
      frequency_unit: frequencyUnit,
      dielectric_constant: parseFloat(dielectricConstant) || 4.4,
      substrate_height: parseFloat(substrateHeight) || 1.6,
      substrate_height_unit: heightUnit,
      advanced: {
        enabled: advancedEnabled,
        feed_impedance: parseFloat(feedImpedance) || 50,
        use_inset_feed: useInsetFeed,
      },
    };
    onSubmit(request);
  };

  return (
    <form onSubmit={handleSubmit} className="form-container">
      
      <div className="section-label">DESIGN PARAMETERS</div>
      
      <div className="form-group-row">
        <label className="form-label" htmlFor="frequency">Resonant Frequency</label>
        <div className="flex-center-gap">
          <input
            id="frequency"
            type="number"
            className="input-minimal"
            value={frequency}
            onChange={(e) => setFrequency(e.target.value)}
            step="any"
          />
          <div className="segmented-control">
            {(['Hz', 'kHz', 'MHz', 'GHz'] as const).map((unit) => (
              <button
                key={unit}
                type="button"
                className={`segment-btn ${frequencyUnit === unit ? 'active' : ''}`}
                onClick={() => setFrequencyUnit(unit)}
              >
                {unit}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="form-group-row">
        <label className="form-label">Substrate Material</label>
        <div className="material-input-group">
          <select
            className="material-preset-select"
            value={presetKey}
            onChange={handlePresetChange}
          >
            {MATERIAL_PRESETS.map((m) => (
              <option key={m.key} value={m.key}>{m.name}</option>
            ))}
          </select>
          <span className="er-label">εr =</span>
          <input
            type="number"
            className="input-minimal"
            value={dielectricConstant}
            onChange={handleDielectricChange}
            step="any"
          />
        </div>
      </div>

      <div className="form-group-row">
        <label className="form-label" htmlFor="height">Substrate Height (h)</label>
        <div className="flex-center-gap">
          <input
            id="height"
            type="number"
            className="input-minimal"
            value={substrateHeight}
            onChange={(e) => setSubstrateHeight(e.target.value)}
            step="any"
          />
          <div className="segmented-control">
            {(['mm', 'cm', 'mil'] as const).map((unit) => (
              <button
                key={unit}
                type="button"
                className={`segment-btn ${heightUnit === unit ? 'active' : ''}`}
                onClick={() => setHeightUnit(unit)}
              >
                {unit}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="section-header-row mt-8">
        <div className="section-label mb-0">ADVANCED MODE</div>
        <label className="toggle-switch">
          <input
            type="checkbox"
            checked={advancedEnabled}
            onChange={(e) => setAdvancedEnabled(e.target.checked)}
          />
          <span className="toggle-slider"></span>
        </label>
      </div>

      <div className={`advanced-section ${advancedEnabled ? 'enabled' : 'disabled'}`}>
        <div className="form-group-row">
          <label className="form-label" htmlFor="impedance">Feed Impedance (Z0)</label>
          <div className="flex-center-gap-sm">
            <input
              id="impedance"
              type="number"
              className="input-minimal"
              value={feedImpedance}
              onChange={(e) => setFeedImpedance(e.target.value)}
              step="any"
            />
            <span className="er-label">Ω</span>
          </div>
        </div>

        <div className="form-group-row mt-2">
          <label className="form-label cursor-pointer" htmlFor="inset-feed">
            <input
              type="checkbox"
              id="inset-feed"
              checked={useInsetFeed}
              onChange={(e) => setUseInsetFeed(e.target.checked)}
              className="checkbox-accent"
            />
            <span className="checkbox-label">Use Inset Feed</span>
          </label>
        </div>
      </div>

      <button
        type="submit"
        className="btn-primary"
        disabled={isLoading}
      >
        {isLoading ? 'Calculating...' : 'Calculate Dimensions'}
      </button>
    </form>
  );
};
