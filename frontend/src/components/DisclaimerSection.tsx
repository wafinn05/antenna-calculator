import React, { useState } from 'react';

export const DisclaimerSection: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="disclaimer-section">
      <div className="collapsible-header" onClick={() => setIsOpen(!isOpen)} role="button" tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setIsOpen(!isOpen)} aria-expanded={isOpen}>
        <h2>📚 About This Model & References</h2>
        <span className={`collapsible-arrow ${isOpen ? 'open' : ''}`}>▼</span>
      </div>

      <div className={`collapsible-body ${isOpen ? 'open' : ''}`}>
        <p>
          This calculator uses the <strong>Transmission Line Model</strong> for rectangular
          microstrip patch antennas operating in the dominant TM₀₁₀ mode. It provides
          analytical closed-form solutions for patch dimensions based on resonant frequency,
          substrate dielectric constant, and substrate height.
        </p>

        <p><strong>Model Validity Range:</strong></p>
        <ul>
          <li>Dielectric constant εr between 2.0 and 10 (common RF substrates)</li>
          <li>Thin substrate assumption: h/λ₀ ≤ 0.05</li>
          <li>Dominant mode TM₀₁₀ only (single-layer, single-element)</li>
          <li>Not suitable for circular polarization, stacked patches, or array configurations</li>
        </ul>

        <p><strong>Important:</strong> Results from this calculator are analytical estimates.
          For production-grade designs, always validate with full-wave electromagnetic simulation
          tools such as CST Studio Suite, Ansys HFSS, or AWR Microwave Office before fabrication.</p>

        <p className="disclaimer-title">
          References
        </p>

        <div className="reference">
          C. A. Balanis, <em>Antenna Theory: Analysis and Design</em>, 4th Edition,
          Chapter 14 — Microstrip Antennas, Transmission Line Model.
        </div>
        <div className="reference">
          E. O. Hammerstad, "Equations for Microstrip Circuit Design,"
          Proc. 5th European Microwave Conference, 1975.
        </div>
        <div className="reference">
          E. Hammerstad and Ø. Jensen, "Accurate Models for Microstrip Computer-Aided Design,"
          IEEE MTT-S International Microwave Symposium, 1980.
        </div>
      </div>
    </div>
  );
};
