import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Html, Bounds } from '@react-three/drei';
import * as THREE from 'three';

export interface PatchAntenna3DProps {
  widthMm: number;        // W
  lengthMm: number;       // L
  substrateHeightMm: number; // h
  groundPlaneWidthMm: number; // Wg
  groundPlaneLengthMm: number; // Lg
  feedLineWidthMm?: number;  // Wf, advanced mode only
  insetDepthMm?: number;     // y0, advanced mode only
  insetGapMm?: number;       // g, advanced mode only
  substrateMaterial: string;
  autoRotate?: boolean;
}

// Substrate Material visual mapping
const getSubstrateMaterialArgs = (materialKey: string) => {
  const key = materialKey.toUpperCase();
  if (key.includes('FR4')) return { color: '#88a382', opacity: 0.65 };
  if (key.includes('RO4003') || key.includes('ROGERS')) return { color: '#d2b48c', opacity: 0.65 };
  if (key.includes('DUROID') || key.includes('RT')) return { color: '#f5f5dc', opacity: 0.65 };
  if (key.includes('ALUMINA')) return { color: '#e0e0e0', opacity: 0.75 };
  if (key.includes('AIR')) return { color: '#e0f7fa', opacity: 0.2 };
  return { color: '#7a8b99', opacity: 0.55 }; // Custom or default
};

const THICKNESS = 0.2; // Visual thickness for copper layers

export const PatchVisualization3D: React.FC<PatchAntenna3DProps> = ({
  widthMm,
  lengthMm,
  substrateHeightMm,
  groundPlaneWidthMm,
  groundPlaneLengthMm,
  feedLineWidthMm,
  insetDepthMm,
  insetGapMm,
  substrateMaterial,
  autoRotate = false
}) => {
  const W = widthMm;
  const L = lengthMm;
  const h = substrateHeightMm;
  const Wg = groundPlaneWidthMm;
  const Lg = groundPlaneLengthMm;
  
  const Wf = feedLineWidthMm || 2.0;
  const y0 = insetDepthMm || 0;
  const g = insetGapMm || (Wf * 0.5); // Default gap if not provided

  const subMatArgs = getSubstrateMaterialArgs(substrateMaterial);

  // Copper material (reused)
  const copperMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#D4915C',
    metalness: 0.8,
    roughness: 0.3
  }), []);

  // Substrate material
  const substrateMaterialObj = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: subMatArgs.color,
    transparent: true,
    opacity: subMatArgs.opacity,
    roughness: 0.6,
    metalness: 0.0,
    transmission: 0.2, // slight glass effect
    thickness: h
  }), [subMatArgs.color, subMatArgs.opacity, h]);

  return (
    <div className="viz-container relative">
      <Canvas camera={{ position: [Wg * 0.8, Math.max(Wg, Lg) * 0.8, Lg * 0.8], fov: 45 }}>
        <color attach="background" args={['#ffffff']} />
        
        <ambientLight intensity={0.6} />
        <directionalLight position={[100, 200, 50]} intensity={1.2} />
        <directionalLight position={[-100, 50, -50]} intensity={0.5} />

        <Bounds fit clip observe margin={1.2}>
          <group>
            
            {/* Ground Plane (centered at Y = -THICKNESS/2) */}
            <mesh position={[0, -THICKNESS / 2, 0]} material={copperMaterial}>
              <boxGeometry args={[Wg, THICKNESS, Lg]} />
            </mesh>

            {/* Substrate (centered at Y = h/2) */}
            <mesh position={[0, h / 2, 0]} material={substrateMaterialObj}>
              <boxGeometry args={[Wg, h, Lg]} />
            </mesh>

            {/* Patch & Feed Line (centered at Y = h + THICKNESS/2) */}
            <group position={[0, h + THICKNESS / 2, 0]}>
              
              {y0 > 0 ? (
                // Inset Feed: build patch out of 3 blocks to leave a notch
                <>
                  {/* Main Body */}
                  <mesh position={[0, 0, -y0 / 2]} material={copperMaterial}>
                    <boxGeometry args={[W, THICKNESS, L - y0]} />
                  </mesh>
                  {/* Left Arm */}
                  <mesh position={[-W/2 + (W - Wf - 2*g)/4, 0, (L - y0)/2]} material={copperMaterial}>
                    <boxGeometry args={[(W - Wf - 2*g)/2, THICKNESS, y0]} />
                  </mesh>
                  {/* Right Arm */}
                  <mesh position={[W/2 - (W - Wf - 2*g)/4, 0, (L - y0)/2]} material={copperMaterial}>
                    <boxGeometry args={[(W - Wf - 2*g)/2, THICKNESS, y0]} />
                  </mesh>
                </>
              ) : (
                // Simple Patch
                <mesh position={[0, 0, 0]} material={copperMaterial}>
                  <boxGeometry args={[W, THICKNESS, L]} />
                </mesh>
              )}

              {/* Feed Line */}
              {/* Length from patch inset (L/2 - y0) to ground plane edge (Lg/2) */}
              <mesh position={[0, 0, (L/2 - y0 + Lg/2)/2]} material={copperMaterial}>
                <boxGeometry args={[Wf, THICKNESS, (Lg/2) - (L/2 - y0)]} />
              </mesh>

            </group>

            {/* Labels */}
            {/* W Label */}
            <Html position={[0, h + THICKNESS, -L/2 - 2]} center zIndexRange={[100, 0]} className="html-label label-blue">
              W = {W.toFixed(2)} mm
            </Html>
            {/* L Label */}
            <Html position={[W/2 + 2, h + THICKNESS, 0]} center zIndexRange={[100, 0]} className="html-label label-blue">
              L = {L.toFixed(2)} mm
            </Html>
            {/* h Label */}
            <Html position={[-Wg/2 - 2, h/2, 0]} center zIndexRange={[100, 0]} className="html-label label-gray">
              h = {h.toFixed(2)} mm
            </Html>

          </group>
        </Bounds>

        <OrbitControls 
          makeDefault
          enablePan={false} 
          enableZoom={true}
          enableRotate={true}
          autoRotate={autoRotate}
          autoRotateSpeed={4.0}
          minDistance={10}
          maxDistance={500}
        />
      </Canvas>
    </div>
  );
};
