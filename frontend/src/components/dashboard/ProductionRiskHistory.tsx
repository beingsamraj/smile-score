/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ShieldAlert } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

const riskColor: Record<string, string> = {
  LOW: '#22c55e',
  MEDIUM: '#eab308',
  HIGH: '#ef4444',
  NO_DATA: '#9ca3af',
};

const riskNumeric: Record<string, number> = {
  LOW: 25,
  MEDIUM: 60,
  HIGH: 90,
  NO_DATA: 0,
};

export default function ProductionRiskHistory() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await fetch(`${API_URL}/api/dashboard/production-risk/history?days=7`, { cache: 'no-store' });
        const json = await res.json();
        const rows = (json.data || []).map((r: any) => ({
          timestamp: new Date(r.timestamp).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }),
          risk_level: r.risk_level,
          risk_score: r.risk_score ?? riskNumeric[r.risk_level] ?? 0,
          fill: riskColor[r.risk_level] ?? '#9ca3af',
        }));
        setData(rows);
      } catch {
        setData([]);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, []);

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center space-x-2 mb-4">
        <ShieldAlert className="w-5 h-5 text-orange-500" />
        <h3 className="text-base font-semibold text-gray-800">Production Risk — Last 7 Days</h3>
      </div>

      {loading ? (
        <div className="h-48 flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500" />
        </div>
      ) : data.length === 0 ? (
        <div className="h-48 flex flex-col items-center justify-center text-gray-400">
          <ShieldAlert className="w-8 h-8 mb-2" />
          <p className="text-sm">No risk data recorded yet.</p>
          <p className="text-xs mt-1">Risk readings will appear here once logged.</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={190}>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="timestamp" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(value: any, _name: any, props: any) => [
                `${props.payload.risk_level} (${value})`, 'Risk Score'
              ]}
            />
            <Area
              type="monotone"
              dataKey="risk_score"
              stroke="#f97316"
              fill="#fed7aa"
              strokeWidth={2}
              name="Risk Score"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* Risk Legend */}
      <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
        {Object.entries(riskColor).filter(([k]) => k !== 'NO_DATA').map(([level, color]) => (
          <span key={level} className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: color }} />
            <span>{level}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
