"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUp, ArrowDown, Activity } from "lucide-react";

// Define data types
interface MarketTick {
  time: string;
  symbol: string;
  price: number;
}

export default function Home() {
  const [latestData, setLatestData] = useState<MarketTick[]>([]);
  const [historyData, setHistoryData] = useState<MarketTick[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState("BTC-USD");
  const [loading, setLoading] = useState(true);

  // Fetch data function
  const fetchData = async () => {
    try {
      // 1. Get latest overview
      const latestRes = await fetch("/api/market/latest");
      const latestJson = await latestRes.json();
      setLatestData(latestJson);

      // 2. Get historical trend for selected asset
      const historyRes = await fetch(`/api/market/history/${selectedSymbol}?limit=50`);
      const historyJson = await historyRes.json();
      // Recharts needs data in chronological order
      setHistoryData(historyJson.reverse());

      setLoading(false);
    } catch (error) {
      console.error("Fetch error:", error);
    }
  };

  // Initial load + periodic refresh (every 5 seconds)
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 p-8">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Header */}
        <div className="flex items-center space-x-3 mb-8">
          <Activity className="w-8 h-8 text-blue-500" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            全球经济情报平台
          </h1>
        </div>

        {/* Market overview cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {latestData.map((item) => (
            <div
              key={item.symbol}
              onClick={() => setSelectedSymbol(item.symbol)}
              className={`p-6 rounded-xl border cursor-pointer transition-all hover:scale-105 ${
                selectedSymbol === item.symbol
                  ? "bg-slate-800 border-blue-500 ring-1 ring-blue-500"
                  : "bg-slate-900 border-slate-800 hover:border-slate-600"
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-slate-400 text-sm font-medium">{item.symbol}</h3>
                  <p className="text-2xl font-bold mt-2">${item.price.toLocaleString()}</p>
                </div>
                {/* Simple up/down simulation icon */}
                <div className={`p-2 rounded-full ${Math.random() > 0.5 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                   {Math.random() > 0.5 ? <ArrowUp size={20} /> : <ArrowDown size={20} />}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Historical trend chart */}
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
          <h2 className="text-xl font-semibold mb-6 flex items-center">
            <span className="text-blue-400 mr-2">{selectedSymbol}</span> 实时走势
          </h2>
          <div className="h-[400px] w-full">
            {loading ? (
              <div className="flex items-center justify-center h-full text-slate-500">加载数据中...</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis
                    dataKey="time"
                    tickFormatter={(time) => new Date(time).toLocaleTimeString()}
                    stroke="#94a3b8"
                    fontSize={12}
                  />
                  <YAxis
                    domain={['auto', 'auto']}
                    stroke="#94a3b8"
                    fontSize={12}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }}
                    labelFormatter={(label) => new Date(label).toLocaleString()}
                  />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 8 }}
                    isAnimationActive={false} // Disable animation for smoother real-time feel
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

      </div>
    </main>
  );
}
