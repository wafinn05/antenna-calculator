import React, { useState } from 'react';
import type { PatchAntennaResponse } from '../types';
import { PatchVisualization } from './PatchVisualization';
import { PatchVisualization3D } from './PatchVisualization3D';
import { ExportButtons } from './ExportButtons';
import { WarningBanner } from './WarningBanner';

interface ResultPanelProps {
  data: PatchAntennaResponse;
}

const fmt = (value: number, decimals: number = 2): string => {
  return value.toFixed(decimals);
};

// Heuristic to guess material from dielectric constant
const guessMaterial = (er: number): string => {
  if (Math.abs(er - 4.4) < 0.1) return 'fr4';
  if (Math.abs(er - 2.2) < 0.1) return 'duroid5880';
  if (Math.abs(er - 10.2) < 0.1) return 'duroid6010';
  if (Math.abs(er - 3.38) < 0.1) return 'rogers4003c';
  if (Math.abs(er - 9.8) < 0.1) return 'alumina';
  if (Math.abs(er - 1.06) < 0.1) return 'air';
  return 'custom';
};

export const ResultPanel: React.FC<ResultPanelProps> = ({ data }) => {
  const [viewMode, setViewMode] = useState<'2D' | '3D'>('2D');

  const { result, advanced_result, model_info, warnings, input_echo } = data;
  const materialKey = guessMaterial(input_echo.dielectric_constant);

  return (
    <div className="result-panel-container">
      
      <WarningBanner warnings={warnings} />

      {/* TOP SECTION: Viz + W/L Cards */}
      <div className="results-top">
        <div className="viz-card">
          
          {/* Header Controls for Viz */}
          <div className="viz-header-controls">
            <div className="segmented-control viz-segmented-control">
              <button 
                className={`segment-btn ${viewMode === '2D' ? 'active' : ''}`}
                onClick={() => setViewMode('2D')}
              >
                2D
              </button>
              <button 
                className={`segment-btn ${viewMode === '3D' ? 'active' : ''}`}
                onClick={() => setViewMode('3D')}
              >
                3D
              </button>
            </div>
          </div>

          {viewMode === '2D' ? (
            <PatchVisualization result={result} />
          ) : (
            <PatchVisualization3D 
              widthMm={result.width_mm}
              lengthMm={result.length_mm}
              substrateHeightMm={input_echo.substrate_height_m * 1000}
              groundPlaneWidthMm={result.recommended_ground_plane.width_mm}
              groundPlaneLengthMm={result.recommended_ground_plane.length_mm}
              feedLineWidthMm={advanced_result?.feed_line_width_mm || undefined}
              insetDepthMm={advanced_result?.inset_feed_depth_mm || undefined}
              substrateMaterial={materialKey}
            />
          )}
        </div>
        
        <div className="dim-cards">
          <div className="dim-card">
            <div className="dim-label">Patch Width (W)</div>
            <div className="dim-value">{fmt(result.width_mm, 2)}<span>mm</span></div>
          </div>
          <div className="dim-card">
            <div className="dim-label">Patch Length (L)</div>
            <div className="dim-value">{fmt(result.length_mm, 2)}<span>mm</span></div>
          </div>
        </div>
      </div>

      {/* BOTTOM SECTION: Tables */}
      <div className="results-bottom">
        {/* Left Column: Electrodynamic */}
        <div className="table-column">
          <div className="section-label">ELECTRODYNAMIC PARAMETERS</div>
          <div className="data-card">
            <div className="data-row">
              <span className="data-key">Effective Dielectric (ε_eff)</span>
              <span className="data-val">{fmt(result.effective_dielectric_constant, 3)}</span>
            </div>
            <div className="data-row">
              <span className="data-key">Fringing Extension (ΔL)</span>
              <span className="data-val">{fmt(result.length_extension_mm, 3)} mm</span>
            </div>
            <div className="data-row">
              <span className="data-key">Effective Length (L_eff)</span>
              <span className="data-val">{fmt(result.effective_length_mm, 3)} mm</span>
            </div>
            <div className="data-row">
              <span className="data-key">Free-space Wavelength (λ0)</span>
              <span className="data-val">{fmt(result.free_space_wavelength_mm, 2)} mm</span>
            </div>
            <div className="data-row">
              <span className="data-key">Guided Wavelength (λg)</span>
              <span className="data-val">{fmt(result.guided_wavelength_mm, 2)} mm</span>
            </div>
          </div>
        </div>

        {/* Right Column: Ground Plane & Feed */}
        <div className="table-column">
          
          <div>
            <div className="section-header-row">
              <div className="section-label">MINIMUM GROUND PLANE</div>
              <div className="badge-gray">Rule: L+6h, W+6h</div>
            </div>
            <div className="ground-plane-box">
              <div className="gp-stat">
                <span className="dim-label mb-1">Width (Wg)</span>
                <span className="data-val">{fmt(result.recommended_ground_plane.width_mm, 2)} mm</span>
              </div>
              <div className="gp-stat">
                <span className="dim-label mb-1">Length (Lg)</span>
                <span className="data-val">{fmt(result.recommended_ground_plane.length_mm, 2)} mm</span>
              </div>
            </div>
          </div>

          {advanced_result && (
            <div className="mt-auto">
              <div className="section-label text-primary">FEED NETWORK (ESTIMATED)</div>
              <div className="data-card data-card-highlight">
                <div className="data-row row-highlight">
                  <span className="data-key">Feed Line Width (Wf)</span>
                  <span className="data-val">{fmt(advanced_result.feed_line_width_mm, 2)} mm</span>
                </div>
                {advanced_result.inset_feed_depth_mm !== null && (
                  <div className="data-row row-highlight">
                    <span className="data-key">Inset Depth (y0)</span>
                    <span className="data-val">{fmt(advanced_result.inset_feed_depth_mm, 2)} mm</span>
                  </div>
                )}
              </div>
            </div>
          )}

        </div>
      </div>

      {/* FOOTER */}
      <div className="app-footer">
        <ExportButtons data={data} />
        <div className="footer-credits">
          {model_info.model} — {model_info.valid_mode}<br />
          <a href="#">About this model</a>
        </div>
      </div>

    </div>
  );
};
