'use client';

import { useState } from 'react';

type DeviceState = 'ON' | 'OFF';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [currentState, setCurrentState] = useState<DeviceState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const toggleDevice = async (targetState: DeviceState) => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('http://localhost:5000/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: targetState }),
      });

      if (!res.ok) throw new Error();

      setCurrentState(targetState);
    } catch {
      setError('Failed to toggle device');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="p-8 min-h-screen bg-gray-100">
      <h1 className="text-2xl font-bold mb-4">Device Controller</h1>

      <div className="space-x-2">
        <button
          onClick={() => toggleDevice('ON')}
          disabled={loading}
          className="px-4 py-2 bg-green-500 text-white rounded disabled:opacity-50"
        >
          Turn On
        </button>

        <button
          onClick={() => toggleDevice('OFF')}
          disabled={loading}
          className="px-4 py-2 bg-red-500 text-white rounded disabled:opacity-50"
        >
          Turn Off
        </button>
      </div>

      <div className="mt-4">
        {loading && <p className="text-gray-600">Updating...</p>}
        {currentState && <p>Current state: {currentState}</p>}
        {error && <p className="text-red-500">{error}</p>}
      </div>
    </main>
  );
}