"use client";

import React, { useEffect, useState, useMemo } from 'react';
import Papa from 'papaparse';
import ItemTable from '@/components/ItemTable';
import Modal from '@/components/Modal';
import ItemDetails from '@/components/ItemDetails';
import SettingsPanel from '@/components/SettingsPanel';
import { ThemeSwitcher } from '@/components/ThemeSwitcher';
import { Item } from '@/types';

type SortMode = 'rank_score' | 'high_volume' | 'high_margin';

const DashboardPage = () => {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortMode, setSortMode] = useState<SortMode>('rank_score');
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [isItemModalOpen, setIsItemModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);

  // Settings state
  const [taxRate, setTaxRate] = useState(0.08);
  const [brokerFee, setBrokerFee] = useState(0.03);
  const [regionId, setRegionId] = useState(10000002); // The Forge

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const res = await fetch(`/api/top-items?region=${regionId}`);
        if (!res.ok) {
          throw new Error('Failed to fetch items');
        }
        const data: Item[] = await res.json();
        setItems(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, [regionId]);

  const sortedItems = useMemo(() => {
    const sorted = [...items];
    if (sortMode === 'high_volume') {
      sorted.sort((a, b) => b.avg_daily_volume - a.avg_daily_volume);
    } else if (sortMode === 'high_margin') {
      sorted.sort((a, b) => b.roi_percent - a.roi_percent);
    }
    return sorted;
  }, [items, sortMode]);

  const filteredItems = useMemo(() => {
    return sortedItems.filter(item =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [sortedItems, searchTerm]);

  const handleRowClick = (itemId: number) => {
    setSelectedItemId(itemId);
    setIsItemModalOpen(true);
  };

  const closeItemModal = () => {
    setIsItemModalOpen(false);
    setSelectedItemId(null);
  };

  const handleSaveSettings = async (newSettings: { taxRate: number; brokerFee: number; regionId: number }) => {
    setTaxRate(newSettings.taxRate);
    setBrokerFee(newSettings.brokerFee);
    setRegionId(newSettings.regionId);
    setIsSettingsModalOpen(false);

    // Trigger a data refresh with the new settings
    setLoading(true);
    try {
      await fetch(`/api/refresh?tax_rate=${newSettings.taxRate}&broker_fee=${newSettings.brokerFee}`, {
        method: 'POST',
      });
      // Refetch items to reflect the new calculations
      const res = await fetch(`/api/top-items?region=${newSettings.regionId}`);
      if (!res.ok) {
        throw new Error('Failed to fetch items after settings change');
      }
      const data: Item[] = await res.json();
      setItems(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCsv = () => {
    const csv = Papa.unparse(filteredItems);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'eve-profit-analyzer-data.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">EVE Profit Analyzer Dashboard</h1>
      <div className="flex justify-between items-center mb-4">
        <div className="w-1/2">
          <input
            type="text"
            placeholder="Search for items..."
            className="w-full p-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex space-x-2">
          <ThemeSwitcher />
          <button
            className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600"
            onClick={handleExportCsv}
          >
            Export CSV
          </button>
          <button
            className="px-4 py-2 rounded-md bg-gray-200 dark:bg-gray-600"
            onClick={() => setIsSettingsModalOpen(true)}
          >
            Settings
          </button>
          <button
            className={`px-4 py-2 rounded-md ${sortMode === 'rank_score' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}
            onClick={() => setSortMode('rank_score')}
          >
            Top Ranked
          </button>
          <button
            className={`px-4 py-2 rounded-md ${sortMode === 'high_volume' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}
            onClick={() => setSortMode('high_volume')}
          >
            High Volume
          </button>
          <button
            className={`px-4 py-2 rounded-md ${sortMode === 'high_margin' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}
            onClick={() => setSortMode('high_margin')}
          >
            High Margin
          </button>
        </div>
      </div>
      {loading ? <p>Loading...</p> : <ItemTable items={filteredItems} onRowClick={handleRowClick} />}
      <Modal isOpen={isItemModalOpen} onClose={closeItemModal}>
        {selectedItemId && <ItemDetails itemId={selectedItemId} />}
      </Modal>
      <Modal isOpen={isSettingsModalOpen} onClose={() => setIsSettingsModalOpen(false)}>
        <SettingsPanel
          initialTaxRate={taxRate}
          initialBrokerFee={brokerFee}
          initialRegionId={regionId}
          onSave={handleSaveSettings}
        />
      </Modal>
    </div>
  );
};

export default DashboardPage;