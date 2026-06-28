import React, { useState, useCallback } from 'react';
import type { PatchAntennaResponse } from '../types';

interface ExportButtonsProps {
  data: PatchAntennaResponse;
}

function formatResultsAsText(data: PatchAntennaResponse): string {
  // ... (keep same logic, just omit the long string copy-paste here for brevity, wait I need to provide full content)
  const { result, input_echo } = data;
  const lines: string[] = [
    'PatchCalc — Microstrip Patch Antenna Results',
    '--------------------------------------------',
    `Frequency:        ${(input_echo.frequency_hz / 1e9).toFixed(4)} GHz`,
    `εr:               ${input_echo.dielectric_constant}`,
    `Substrate Height: ${(input_echo.substrate_height_m * 1000).toFixed(3)} mm`,
    `Width (W):        ${result.width_mm.toFixed(4)} mm`,
    `Length (L):       ${result.length_mm.toFixed(4)} mm`,
  ];
  return lines.join('\n');
}

function generateCSV(data: PatchAntennaResponse): string {
  const { result, input_echo } = data;
  return `Parameter,Value,Unit\nFrequency,${input_echo.frequency_hz/1e9},GHz\nWidth,${result.width_mm},mm\nLength,${result.length_mm},mm`;
}

export const ExportButtons: React.FC<ExportButtonsProps> = ({ data }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    const text = formatResultsAsText(data);
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
    }
  }, [data]);

  const handleDownloadCSV = useCallback(() => {
    const csv = generateCSV(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'patch_antenna.csv';
    link.click();
    URL.revokeObjectURL(url);
  }, [data]);

  return (
    <div className="export-btns">
      <button className={`btn-outline ${copied ? 'copied' : ''}`} onClick={handleCopy}>
        {copied ? 'Copied' : 'Copy'}
      </button>
      <button className="btn-outline" onClick={handleDownloadCSV}>
        CSV
      </button>
    </div>
  );
};
