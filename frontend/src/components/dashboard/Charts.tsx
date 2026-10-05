/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export function SmileTrendChart({ data, forecast }: { data: any, forecast?: any }) {
  if (!data || !data.data) return <div className="p-4 bg-white rounded-xl border h-64 flex items-center justify-center">Loading...</div>;
  if (data.data.length === 0) return <div className="p-4 bg-white rounded-xl border h-64 flex items-center justify-center text-gray-500">No smile-score data available for this period.</div>;

  // Combine historical and forecast data
  let combinedData = [...data.data];
  if (forecast && forecast.data && forecast.data.length > 0) {
    // Add forecast points with a flag
    const forecastPoints = forecast.data.map((p: any) => ({
      timestamp: p.timestamp,
      forecast_score: p.smile_score,
      isForecast: true
    }));
    
    // To make the line continuous, add the last historical point as the start of forecast
    if (combinedData.length > 0) {
      const lastHist = combinedData[combinedData.length - 1];
      forecastPoints.unshift({
        timestamp: lastHist.timestamp,
        forecast_score: lastHist.smile_score,
        isForecast: true
      });
    }
    
    combinedData = [...combinedData, ...forecastPoints];
  }

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 h-80">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Smile Score Trend & Forecast</h3>
        {forecast && forecast.data && forecast.data.length > 0 && (
          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full flex items-center">
            <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mr-1.5 animate-pulse" />
            AI Forecast Active
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height="80%">
        <LineChart data={combinedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={(tick) => {
              const d = new Date(tick as string | number);
              return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
            }}
            tick={{ fontSize: 11 }}
          />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
          <Tooltip 
            labelFormatter={(label) => new Date(label as string | number).toLocaleString()} 
            formatter={(value: any, name: any) => [value, name === 'smile_score' ? 'Historical Score' : 'Predicted Score']}
          />
          <Line type="monotone" dataKey="smile_score" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} connectNulls />
          <Line type="monotone" dataKey="forecast_score" stroke="#a855f7" strokeWidth={2} strokeDasharray="5 5" dot={{ r: 0 }} connectNulls />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function EmotionDistribution({ data }: { data: any }) {
  if (!data) return <div className="p-4 bg-white rounded-xl border h-64 flex items-center justify-center">Loading...</div>;
  if (data.total === 0) return <div className="p-4 bg-white rounded-xl border h-64 flex items-center justify-center text-gray-500">No data available</div>;

  const chartData = [
    { name: 'Happy', value: data.happy, color: '#16a34a' },
    { name: 'OK', value: data.ok, color: '#ca8a04' },
    { name: 'Sad', value: data.sad, color: '#dc2626' },
  ];

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 h-80 flex flex-col">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Emotion Distribution</h3>
      <div className="flex-1 flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={chartData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="flex justify-center space-x-4 mt-2">
        {chartData.map(entry => (
          <div key={entry.name} className="flex items-center text-sm">
            <span className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: entry.color }}></span>
            {entry.name}: {entry.value}
          </div>
        ))}
      </div>
    </div>
  );
}
