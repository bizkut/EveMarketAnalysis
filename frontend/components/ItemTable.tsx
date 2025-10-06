import React from 'react';
import { Item } from '@/types';

interface ItemTableProps {
  items: Item[];
  onRowClick: (itemId: number) => void;
}

const ItemTable: React.FC<ItemTableProps> = ({ items, onRowClick }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white dark:bg-gray-800">
        <thead>
          <tr className="w-full h-16 border-gray-300 dark:border-gray-500 border-b py-8">
            <th className="text-left pl-4">Item</th>
            <th className="text-left pl-4">Buy Price</th>
            <th className="text-left pl-4">Sell Price</th>
            <th className="text-left pl-4">Profit per Unit</th>
            <th className="text-left pl-4">ROI%</th>
            <th className="text-left pl-4">Volume</th>
            <th className="text-left pl-4">Volatility</th>
            <th className="text-left pl-4">Predicted Sell Price</th>
            <th className="text-left pl-4">Confidence</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.type_id}
              className="h-14 border-gray-300 dark:border-gray-500 border-b cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={() => onRowClick(item.type_id)}
            >
              <td className="pl-4">{item.name}</td>
              <td className="pl-4">{item.buy_price.toFixed(2)}</td>
              <td className="pl-4">{item.sell_price.toFixed(2)}</td>
              <td className="pl-4">{item.profit_per_unit.toFixed(2)}</td>
              <td className="pl-4">{item.roi_percent.toFixed(2)}%</td>
              <td className="pl-4">{item.avg_daily_volume.toLocaleString()}</td>
              <td className="pl-4">{item.volatility.toFixed(2)}</td>
              <td className="pl-4">{item.predicted_sell_price?.toFixed(2)}</td>
              <td className="pl-4">{item.confidence_score?.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ItemTable;