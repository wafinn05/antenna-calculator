/**
 * PatchCalc — API Client
 *
 * Handles communication with the FastAPI backend.
 * All physics calculations are done server-side.
 */

import axios from 'axios';
import type { PatchAntennaRequest, PatchAntennaResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

/**
 * Calculate patch antenna dimensions via backend API.
 */
export async function calculatePatchAntenna(
  request: PatchAntennaRequest
): Promise<PatchAntennaResponse> {
  const response = await apiClient.post<PatchAntennaResponse>(
    '/api/v1/patch-antenna/calculate',
    request
  );
  return response.data;
}

/**
 * Health check for the backend API.
 */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await apiClient.get('/api/v1/patch-antenna/health');
  return response.data;
}
