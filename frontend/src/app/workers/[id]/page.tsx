/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, User, Activity, TrendingUp, Calendar, Smile, Meh, Frown } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts';
import Navbar from '@/components/Navbar';
import { getSession } from '@/../lib/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

interface DailySummary {
  date: string;
  happy: number;
  ok: number;
  sad: number;
  avg_smile_score: number;
  total: number;
}

interface EmotionEvent {
  emotion_id: string;
  emotion: string;
  smile_score: number | null;
  created_at: string;
}

interface WorkerTimeline {
  worker: any;
  period_days: number;
  total_events: number;
  overall_smile_score: number;
  daily: DailySummary[];
  events: EmotionEvent[];
}

const emotionIcon = (emotion: string) => {
  if (emotion === 'happy') return <Smile className="w-4 h-4 text-green-500" />;
  if (emotion === 'sad') return <Frown className="w-4 h-4 text-red-500" />;
  return <Meh className="w-4 h-4 text-yellow-500" />;
};

const emotionColor = (emotion: string) => {
  if (emotion === 'happy') return 'bg-green-100 text-green-800';
  if (emotion === 'sad') return 'bg-red-100 text-red-800';
  return 'bg-yellow-100 text-yellow-800';
};

export default function WorkerTimelinePage() {
  const params = useParams();
  const router = useRouter();
  const workerId = params?.id as string;

  const [loadingAuth, setLoadingAuth] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<WorkerTimeline | null>(null);
  const [days, setDays] = useState(7);

  useEffect(() => {
    async function checkAuth() {
      const { data } = await getSession();
      if (!data?.session) { router.push('/login'); return; }
      setLoadingAuth(false);
    }
    checkAuth();
  }, [router]);

  useEffect(() => {
    if (loadingAuth || !workerId) return;
    async function fetchTimeline() {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`${API_URL}/api/workers/${workerId}/timeline?days=${days}`, { cache: 'no-store' });
        if (!res.ok) throw new Error(res.status === 404 ? 'Worker not found' : 'Failed to fetch timeline');
        setData(await res.json());
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    fetchTimeline();
  }, [workerId, days, loadingAuth]);

  if (loadingAuth) return <div className="min-h-screen flex items-center justify-center bg-gray-50">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">

        {/* Back button */}
        <button onClick={() => router.back()} className="flex items-center text-gray-500 hover:text-gray-800 mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Workers
        </button>

        {loading ? (
          <div className="bg-white rounded-xl border border-gray-200 p-10 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3" />
            <p className="text-gray-500">Loading wellness timeline...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-xl p-10 text-center">
            <p className="text-red-700 font-medium">{error}</p>
            <button onClick={() => router.back()} className="mt-4 text-red-600 underline">Go back</button>
          </div>
        ) : data ? (
          <>
            {/* Worker Header */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center space-x-4">
                <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-7 h-7 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">{data.worker.name}</h1>
                  <p className="text-sm text-gray-500">{data.worker.designation || 'Worker'} · ID: {data.worker.worker_id}</p>
                  <span className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full font-medium ${data.worker.status ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                    {data.worker.status ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              {/* Period Selector */}
              <div className="flex items-center space-x-2 text-sm">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span className="text-gray-500">Period:</span>
                {[7, 14, 30].map(d => (
                  <button
                    key={d}
                    onClick={() => setDays(d)}
                    className={`px-3 py-1 rounded-full border transition-colors ${days === d ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'}`}
                  >
                    {d}d
                  </button>
                ))}
              </div>
            </div>

            {/* KPI Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
              {[
                { label: 'Smile Score', value: data.overall_smile_score, icon: <Activity className="w-5 h-5 text-blue-500" />, color: 'text-blue-700' },
                { label: 'Total Readings', value: data.total_events, icon: <TrendingUp className="w-5 h-5 text-purple-500" />, color: 'text-purple-700' },
                { label: 'Happy Days', value: data.daily.filter(d => d.happy >= d.ok && d.happy >= d.sad).length, icon: <Smile className="w-5 h-5 text-green-500" />, color: 'text-green-700' },
                { label: 'Days Tracked', value: data.daily.length, icon: <Calendar className="w-5 h-5 text-orange-500" />, color: 'text-orange-700' },
              ].map((kpi) => (
                <div key={kpi.label} className="bg-white rounded-xl border border-gray-200 p-4 flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gray-50 rounded-lg flex items-center justify-center">{kpi.icon}</div>
                  <div>
                    <p className={`text-2xl font-bold ${kpi.color}`}>{kpi.value}</p>
                    <p className="text-xs text-gray-500">{kpi.label}</p>
                  </div>
                </div>
              ))}
            </div>

            {data.daily.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center text-gray-500">
                <Activity className="w-10 h-10 mx-auto mb-3 text-gray-300" />
                <p className="font-medium text-gray-700">No emotion data recorded</p>
                <p className="text-sm mt-1">No emotion readings found for this worker in the last {days} days.</p>
              </div>
            ) : (
              <>
                {/* Smile Score Trend Line Chart */}
                <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
                  <h2 className="text-base font-semibold text-gray-800 mb-4">Smile Score Trend</h2>
                  <ResponsiveContainer width="100%" height={220}>
                    <LineChart data={data.daily}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Line type="monotone" dataKey="avg_smile_score" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} name="Avg Smile Score" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Daily Emotion Breakdown Bar Chart */}
                <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
                  <h2 className="text-base font-semibold text-gray-800 mb-4">Daily Emotion Breakdown</h2>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={data.daily}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="happy" fill="#22c55e" name="Happy" stackId="a" />
                      <Bar dataKey="ok" fill="#eab308" name="OK" stackId="a" />
                      <Bar dataKey="sad" fill="#ef4444" name="Sad" stackId="a" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Recent Events Log */}
                <div className="bg-white rounded-xl border border-gray-200 p-6">
                  <h2 className="text-base font-semibold text-gray-800 mb-4">Recent Emotion Events</h2>
                  {data.events.length === 0 ? (
                    <p className="text-gray-500 text-sm">No recent events.</p>
                  ) : (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {[...data.events].reverse().map((ev) => (
                        <div key={ev.emotion_id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                          <div className="flex items-center space-x-3">
                            {emotionIcon(ev.emotion)}
                            <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${emotionColor(ev.emotion)}`}>
                              {ev.emotion}
                            </span>
                            {ev.smile_score !== null && (
                              <span className="text-sm text-gray-600">Score: <strong>{ev.smile_score}</strong></span>
                            )}
                          </div>
                          <span className="text-xs text-gray-400">
                            {new Date(ev.created_at).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' })}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}
          </>
        ) : null}
      </main>
    </div>
  );
}
