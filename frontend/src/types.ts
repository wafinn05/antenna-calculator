/**
 * PatchCalc — TypeScript Types
 *
 * These types mirror the Pydantic schemas from the backend.
 * All calculation results come from the backend API — frontend
 * does NOT perform physics calculations.
 */

// =============================================================================
// Enums
// =============================================================================

export type FrequencyUnit = 'Hz' | 'kHz' | 'MHz' | 'GHz';
export type LengthUnit = 'mm' | 'cm' | 'm' | 'inch' | 'mil' | 'um';

// =============================================================================
// Request Types
// =============================================================================

export interface AdvancedConfig {
  enabled: boolean;
  feed_impedance: number;
  use_inset_feed: boolean;
}

export interface PatchAntennaRequest {
  frequency: number;
  frequency_unit: FrequencyUnit;
  dielectric_constant: number;
  substrate_height: number;
  substrate_height_unit: LengthUnit;
  advanced: AdvancedConfig;
}

// =============================================================================
// Response Types
// =============================================================================

export interface InputEcho {
  frequency_hz: number;
  dielectric_constant: number;
  substrate_height_m: number;
}

export interface RecommendedGroundPlane {
  length_mm: number;
  width_mm: number;
}

export interface MainResult {
  width_mm: number;
  length_mm: number;
  effective_dielectric_constant: number;
  length_extension_mm: number;
  effective_length_mm: number;
  free_space_wavelength_mm: number;
  guided_wavelength_mm: number;
  recommended_ground_plane: RecommendedGroundPlane;
}

export interface AdvancedResult {
  conductance_g1: number;
  edge_resistance_ohm: number;
  inset_feed_depth_mm: number | null;
  feed_line_width_mm: number;
  bandwidth_percent: number;
  directivity_dbi: number;
  w_over_lambda0: number;
}

export interface ModelInfo {
  model: string;
  valid_mode: string;
  assumptions: string;
}

export interface PatchAntennaResponse {
  input_echo: InputEcho;
  result: MainResult;
  advanced_result: AdvancedResult | null;
  warnings: string[];
  model_info: ModelInfo;
}

// =============================================================================
// Material Presets
// =============================================================================

export interface MaterialPreset {
  key: string;
  name: string;
  epsilon_r: number;
}

export const MATERIAL_PRESETS: MaterialPreset[] = [
  { key: 'FR4', name: 'FR-4 Glass', epsilon_r: 4.4 },
  { key: 'RT5880', name: 'RT/duroid 5880', epsilon_r: 2.2 },
  { key: 'RT6010', name: 'RT/duroid 6010', epsilon_r: 10.2 },
  { key: 'RO4003C', name: 'Rogers RO4003C', epsilon_r: 3.38 },
  { key: 'ALUMINA', name: 'Alumina', epsilon_r: 9.8 },
  { key: 'AIR_FOAM', name: 'Air / Foam', epsilon_r: 1.06 },
  { key: 'CUSTOM', name: 'Custom...', epsilon_r: 0 },
];
