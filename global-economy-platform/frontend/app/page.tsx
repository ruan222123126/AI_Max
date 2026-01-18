"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUp, ArrowDown, Activity, Sparkles, Loader2 } from "lucide-react";

// Define data types
interface MarketTick {
  time: string;
  symbol: string;
  price: number;
}

interface AIAnalysisResponse {
  symbol: string;
  analysis: string;
  generated_at: string;
}

export default function Home() {
  const [latestData, setLatestData] = useState<MarketTick[]>([]);
  const [historyData, setHistoryData] = useState<MarketTick[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState("BTC-USD");
  const [loading, setLoading] = useState(true);

  // AI 分析相关状态
  const [aiAnalysis, setAiAnalysis] = useState<string>("");
  const [aiLoading, setAiLoading] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);

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

  // AI 分析函数
  const fetchAIAnalysis = async () => {
    setAiLoading(true);
    setShowAnalysis(true);
    setAiAnalysis(""); // 清空之前的分析

    try {
      const response = await fetch("/api/ai/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ symbol: selectedSymbol }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: AIAnalysisResponse = await response.json();

      // 打字机效果显示分析结果
      const text = data.analysis;
      let index = 0;
      const speed = 10; // 打字速度（毫秒）

      const typeWriter = () => {
        if (index < text.length) {
          setAiAnalysis((prev) => prev + text.charAt(index));
          index++;
          setTimeout(typeWriter, speed);
        } else {
          setAiLoading(false);
        }
      };

      typeWriter();
    } catch (error) {
      console.error("AI Analysis error:", error);
      setAiAnalysis("❌ 分析失败：无法获取 AI 分析结果。请检查后端服务是否正常运行，以及 API 密钥是否配置正确。");
      setAiLoading(false);
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

        {/* AI 智能分析区域 */}
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold flex items-center">
              <Sparkles className="w-6 h-6 text-purple-400 mr-2" />
              AI 智能分析
            </h2>
            <button
              onClick={fetchAIAnalysis}
              disabled={aiLoading}
              className={`flex items-center space-x-2 px-6 py-2 rounded-lg font-medium transition-all ${
                aiLoading
                  ? "bg-slate-700 text-slate-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 hover:scale-105"
              }`}
            >
              {aiLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>分析中...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>生成分析报告</span>
                </>
              )}
            </button>
          </div>

          {/* AI 分析结果显示区域 */}
          {showAnalysis && (
            <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
              {aiLoading && aiAnalysis === "" ? (
                <div className="flex items-center justify-center py-12 text-slate-400">
                  <Loader2 className="w-8 h-8 animate-spin mr-3" />
                  <span>AI 正在分析市场数据...</span>
                </div>
              ) : (
                <div className="prose prose-invert max-w-none">
                  <div
                    className="markdown-content"
                    dangerouslySetInnerHTML={{
                      __html: aiAnalysis
                        .replace(/\n/g, '<br/>')
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/### (.*?)(<br\/>|$)/g, '<h3 class="text-lg font-bold text-purple-400 mt-4 mb-2">$1</h3>')
                        .replace(/## (.*?)(<br\/>|$)/g, '<h2 class="text-xl font-bold text-blue-400 mt-6 mb-3">$1</h2>')
                        .replace(/- (.*?)(<br\/>|$)/g, '<li class="ml-4">$1</li>')
                    }}
                  />
                </div>
              )}
            </div>
          )}
        </div>

      </div>
    </main>
  );
}
