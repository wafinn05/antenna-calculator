import React from 'react';
import type { MainResult } from '../types';

interface PatchVisualizationProps {
  result: MainResult;
}

export const PatchVisualization: React.FC<PatchVisualizationProps> = ({ result }) => {
  const { width_mm, length_mm, recommended_ground_plane } = result;

  const svgWidth = 400;
  const svgHeight = 180;
  const padding = 40;

  const gpW = recommended_ground_plane.width_mm;
  const gpL = recommended_ground_plane.length_mm;

  const maxDim = Math.max(gpW, gpL);
  const scale = (Math.min(svgWidth, svgHeight) - padding * 2) / maxDim;

  const gw = gpW * scale;
  const gl = gpL * scale;
  const pw = width_mm * scale;
  const pl = length_mm * scale;

  const cx = svgWidth / 2;
  const cy = svgHeight / 2;

  const gx = cx - gw / 2;
  const gy = cy - gl / 2;

  const px = cx - pw / 2;
  const py = cy - pl / 2;

  const dimOffset = 16;

  return (
    <div className="viz-container">
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        preserveAspectRatio="xMidYMid meet"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <marker id="arrow" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto-start-reverse">
            <path d="M 0 0 L 6 3 L 0 6 z" fill="#007aff" />
          </marker>
        </defs>

        {/* Ground plane */}
        <rect
          x={gx} y={gy} width={gw} height={gl}
          fill="none"
          stroke="#cccccc"
          strokeWidth="1"
          strokeDasharray="4 4"
        />
        <text
          x={cx} y={gy - 24}
          textAnchor="middle" fill="#888" fontSize="13" fontFamily="var(--font-sans)"
        >
          Ground Plane
        </text>

        {/* Patch */}
        <rect
          x={px} y={py} width={pw} height={pl}
          fill="#e6f2ff"
          stroke="#007aff"
          strokeWidth="2"
        />
        
        {/* Feed lines mock (just for visual representation like the image) */}
        <line x1={cx - 4} y1={py + pl} x2={cx - 4} y2={gy + gl + 10} stroke="#007aff" strokeWidth="2" />
        <line x1={cx + 4} y1={py + pl} x2={cx + 4} y2={gy + gl + 10} stroke="#007aff" strokeWidth="2" />

        {/* W Dimension */}
        <line
          x1={px} y1={py - dimOffset}
          x2={px + pw} y2={py - dimOffset}
          stroke="#007aff" strokeWidth="1"
          markerStart="url(#arrow)" markerEnd="url(#arrow)"
        />
        <line x1={px} y1={py} x2={px} y2={py - dimOffset - 5} stroke="#007aff" strokeWidth="0.5" strokeDasharray="2 2" />
        <line x1={px + pw} y1={py} x2={px + pw} y2={py - dimOffset - 5} stroke="#007aff" strokeWidth="0.5" strokeDasharray="2 2" />
        
        <rect x={cx - 30} y={py - dimOffset - 8} width="60" height="16" fill="#fff" />
        <text
          x={cx} y={py - dimOffset + 3}
          textAnchor="middle" fill="#007aff" fontSize="10" fontWeight="600" fontFamily="var(--font-sans)"
        >
          W = {width_mm.toFixed(2)}
        </text>

        {/* L Dimension */}
        <line
          x1={px + pw + dimOffset} y1={py}
          x2={px + pw + dimOffset} y2={py + pl}
          stroke="#007aff" strokeWidth="1"
          markerStart="url(#arrow)" markerEnd="url(#arrow)"
        />
        <line x1={px + pw} y1={py} x2={px + pw + dimOffset + 5} y2={py} stroke="#007aff" strokeWidth="0.5" strokeDasharray="2 2" />
        <line x1={px + pw} y1={py + pl} x2={px + pw + dimOffset + 5} y2={py + pl} stroke="#007aff" strokeWidth="0.5" strokeDasharray="2 2" />
        
        <rect x={px + pw + dimOffset - 8} y={cy - 20} width="16" height="40" fill="#fff" />
        <text
          x={px + pw + dimOffset + 8} y={cy}
          textAnchor="middle" fill="#007aff" fontSize="10" fontWeight="600" fontFamily="var(--font-sans)"
          style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
        >
          L = {length_mm.toFixed(2)}
        </text>

        {/* Expand Text mock */}
        <text x={svgWidth - 40} y={40} textAnchor="end" fill="#007aff" fontSize="12" fontFamily="var(--font-sans)">
          Expand
        </text>

      </svg>
    </div>
  );
};
