"use client";

import React, { useState, useEffect } from 'react';

interface Region {
  region_id: number;
  name: string;
}

interface SettingsPanelProps {
  initialTaxRate: number;
  initialBrokerFee: number;
  initialRegionId: number;
  onSave: (settings: { taxRate: number; brokerFee: number; regionId: number }) => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  initialTaxRate,
  initialBrokerFee,
  initialRegionId,
  onSave,
}) => {
  const [taxRate, setTaxRate] = useState(initialTaxRate);
  const [brokerFee, setBrokerFee] = useState(initialBrokerFee);
  const [regionId, setRegionId] = useState(initialRegionId);
  const [regions, setRegions] = useState<Region[]>([]);

  useEffect(() => {
    const fetchRegions = async () => {
      try {
        const res = await fetch('/api/regions');
        if (!res.ok) {
          throw new Error('Failed to fetch regions');
        }
        const data: Region[] = await res.json();
        setRegions(data);
      } catch (error) {
        console.error(error);
      }
    };
    fetchRegions();
  }, []);

  const handleSave = () => {
    onSave({ taxRate, brokerFee, regionId });
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Settings</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Tax Rate (%)</label>
          <input
            type="number"
            className="w-full p-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
            value={taxRate * 100}
            onChange={(e) => setTaxRate(parseFloat(e.target.value) / 100)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Broker Fee (%)</label>
          <input
            type="number"
            className="w-full p-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
            value={brokerFee * 100}
            onChange={(e) => setBrokerFee(parseFloat(e.target.value) / 100)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Region</label>
          <select
            className="w-full p-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
            value={regionId}
            onChange={(e) => setRegionId(parseInt(e.target.value))}
          >
            {regions.map((region) => (
              <option key={region.region_id} value={region.region_id}>
                {region.name}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={handleSave}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded-md"
        >
          Save
        </button>
      </div>
    </div>
  );
};

export default SettingsPanel;