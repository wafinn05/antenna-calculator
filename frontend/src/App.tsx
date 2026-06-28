import React, { useState, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { calculatePatchAntenna } from './api';
import type { PatchAntennaRequest, PatchAntennaResponse } from './types';
import { InputForm } from './components/InputForm';
import { ResultPanel } from './components/ResultPanel';

const App: React.FC = () => {
  const [result, setResult] = useState<PatchAntennaResponse | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: calculatePatchAntenna,
    onSuccess: (data) => {
      setResult(data);
      setApiError(null);
    },
    onError: (error: any) => {
      setResult(null);
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          setApiError(detail);
        } else if (Array.isArray(detail)) {
          setApiError(detail.map((d: any) => d.msg || d.message || JSON.stringify(d)).join('; '));
        } else {
          setApiError(JSON.stringify(detail));
        }
      } else if (error.message) {
        setApiError(`Connection error: ${error.message}`);
      } else {
        setApiError('An unexpected error occurred.');
      }
    },
  });

  const handleSubmit = useCallback(
    (request: PatchAntennaRequest) => {
      mutation.mutate(request);
    },
    [mutation]
  );

  return (
    <div className="app-container">
      {/* LEFT SIDEBAR */}
      <div className="app-sidebar">
        <div className="sidebar-header">
          <div className="logo-box">img</div>
          <div className="header-text">
            <h1>PatchCalc</h1>
            <p>Microstrip Patch Antenna Calculator</p>
          </div>
        </div>
        <div className="sidebar-content">
          <InputForm onSubmit={handleSubmit} isLoading={mutation.isPending} />
        </div>
      </div>

      {/* RIGHT MAIN CONTENT */}
      <div className="app-main">
        {apiError && (
          <div className="error-banner">
            ❌ {apiError}
          </div>
        )}

        {mutation.isPending && (
          <div className="empty-state">
            <p>Calculating...</p>
          </div>
        )}

        {result && !mutation.isPending && (
          <ResultPanel data={result} />
        )}

        {!result && !mutation.isPending && !apiError && (
          <div className="empty-state">
            <h3>Ready to calculate</h3>
            <p>Enter parameters on the left and click Calculate Dimensions.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
