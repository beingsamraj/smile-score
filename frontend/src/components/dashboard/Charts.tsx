/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export function SmileTrendChart({ data }: { data: any }) {
  if (!data || !data.data) return <div className="p-4 bg-white rounded-xl border h-64 flex items-center justify-center">Loading...</div>;
  if (data.data.length === 0) return <div className="p-4 bg-white rounded-xl border h-64 flex items-center justify-center text-gray-500">No smile-score data available for this period.</div>;

  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 h-80">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Smile Score Trend ({data.period})</h3>
      <ResponsiveContainer width="100%" height="80%">
        <LineChart data={data.data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" tickFormatter={(tick) => new Date(tick as string | number).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} />
          <YAxis domain={[0, 100]} />
          <Tooltip labelFormatter={(label) => new Date(label as string | number).toLocaleString()} />
          <Line type="monotone" dataKey="smile_score" stroke="#2563eb" strokeWidth={2} />
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
