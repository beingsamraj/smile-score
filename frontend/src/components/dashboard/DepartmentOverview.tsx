'use client';

import { useEffect, useState } from 'react';
import { BarChart2, Users, TrendingUp } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

interface DeptRow {
  department_id: string;
  department_name: string;
  active_workers: number;
  avg_smile_score: number;
  happy_percentage: number;
  total_emotions_today: number;
}

export default function DepartmentOverview() {
  const [data, setData] = useState<DeptRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDepts() {
      try {
        const res = await fetch(`${API_URL}/api/dashboard/department-overview`, { cache: 'no-store' });
        const json = await res.json();
        setData(json.data || []);
      } catch {
        setData([]);
      } finally {
        setLoading(false);
      }
    }
    fetchDepts();
  }, []);

  const getRankBadge = (index: number) => {
    if (index === 0) return '🥇';
    if (index === 1) return '🥈';
    if (index === 2) return '🥉';
    return `${index + 1}`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-700 bg-green-100';
    if (score >= 40) return 'text-yellow-700 bg-yellow-100';
    if (score > 0) return 'text-red-700 bg-red-100';
    return 'text-gray-500 bg-gray-100';
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center space-x-2 mb-4">
        <BarChart2 className="w-5 h-5 text-blue-500" />
        <h3 className="text-base font-semibold text-gray-800">Department Leaderboard</h3>
      </div>

      {loading ? (
        <div className="h-48 flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
        </div>
      ) : data.length === 0 ? (
        <div className="h-48 flex flex-col items-center justify-center text-gray-400">
          <BarChart2 className="w-8 h-8 mb-2" />
          <p className="text-sm">No department data yet.</p>
          <p className="text-xs mt-1">Add departments to see the leaderboard.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data.map((dept, i) => (
            <div key={dept.department_id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <span className="text-base w-7 text-center font-semibold text-gray-600">{getRankBadge(i)}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">{dept.department_name}</p>
                <div className="flex items-center space-x-3 mt-0.5">
                  <span className="flex items-center text-xs text-gray-500">
                    <Users className="w-3 h-3 mr-0.5" />
                    {dept.active_workers} workers
                  </span>
                  <span className="flex items-center text-xs text-gray-500">
                    <TrendingUp className="w-3 h-3 mr-0.5" />
                    {dept.total_emotions_today} readings today
                  </span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${getScoreColor(dept.avg_smile_score)}`}>
                  {dept.avg_smile_score > 0 ? `${dept.avg_smile_score}` : 'No data'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-400 mt-3">Ranked by average smile score · Last 24 hours</p>
    </div>
  );
}
