export interface Item {
  type_id: number;
  name: string;
  buy_price: number;
  sell_price: number;
  profit_per_unit: number;
  roi_percent: number;
  avg_daily_volume: number;
  volatility: number;
  predicted_sell_price: number | null;
  confidence_score: number | null;
}