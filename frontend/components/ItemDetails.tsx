"use client";

import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Item } from '@/types';

interface ItemDetailsProps {
  itemId: number;
}

interface ItemDetailData {
  item: Item;
  history: { date: string; price: number; volume: number }[];
}

const ItemDetails: React.FC<ItemDetailsProps> = ({ itemId }) => {
  const [data, setData] = useState<ItemDetailData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!itemId) return;

    const fetchItemDetails = async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/item/${itemId}`);
        if (!res.ok) {
          throw new Error('Failed to fetch item details');
        }
        const itemData: ItemDetailData = await res.json();
        setData(itemData);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchItemDetails();
  }, [itemId]);

  if (loading) return <p>Loading item details...</p>;
  if (!data) return <p>No data found for this item.</p>;

  const { item, history } = data;

  return (
    <div>
      <h2 className="text-xl font-bold mb-2">{item.name}</h2>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p><strong>Buy Price:</strong> {item.buy_price.toFixed(2)}</p>
          <p><strong>Sell Price:</strong> {item.sell_price.toFixed(2)}</p>
          <p><strong>Profit per Unit:</strong> {item.profit_per_unit.toFixed(2)}</p>
        </div>
        <div>
          <p><strong>ROI:</strong> {item.roi_percent.toFixed(2)}%</p>
          <p><strong>Avg. Daily Volume:</strong> {item.avg_daily_volume.toLocaleString()}</p>
          <p><strong>Volatility:</strong> {item.volatility.toFixed(2)}</p>
        </div>
      </div>
      <h3 className="text-lg font-semibold mb-2">30-Day Price History</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={history}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="price" stroke="#8884d8" activeDot={{ r: 8 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ItemDetails;