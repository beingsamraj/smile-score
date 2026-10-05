/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable react-hooks/immutability */
'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, RefreshCw, AlertTriangle, Wifi, WifiOff } from 'lucide-react';
import { getSession } from '@/../lib/auth';
import { 
  getDashboardOverview, getSmileTrend, getEmotionDistribution, 
  getWorkers, getAlerts, getRecentActivity, getSmileForecast
} from '@/../lib/dashboardApi';
import KPIOverview from '@/components/dashboard/KPIOverview';
import { SmileTrendChart, EmotionDistribution } from '@/components/dashboard/Charts';
import { WorkerStatus, AlertsPanel, RecentActivity } from '@/components/dashboard/Tables';
import ProductionRiskHistory from '@/components/dashboard/ProductionRiskHistory';
import DepartmentOverview from '@/components/dashboard/DepartmentOverview';
import Navbar from '@/components/Navbar';

const WS_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000').replace(/^http/, 'ws');

export default function DashboardPage() {
  const router = useRouter();
  const [session, setSession] = useState<any>(null);
  const [loadingAuth, setLoadingAuth] = useState(true);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [overviewData, setOverviewData] = useState<any>(null);
  const [trendData, setTrendData] = useState<any>(null);
  const [forecastData, setForecastData] = useState<any>(null);
  const [emotionData, setEmotionData] = useState<any>(null);
  const [workersData, setWorkersData] = useState<any>(null);
  const [alertsData, setAlertsData] = useState<any>(null);
  const [activityData, setActivityData] = useState<any>(null);

  useEffect(() => {
    async function checkAuth() {
      try {
        const { data, error } = await getSession();
        if (error || !data.session) { router.push('/login'); return; }
        setSession(data.session);
      } catch {
        router.push('/login');
      } finally {
        setLoadingAuth(false);
      }
    }
    checkAuth();
  }, [router]);

  const fetchDashboardData = useCallback(async () => {
    try {
      setError(null);
      const [overview, trend, forecast, emotion, workers, alerts, activity] = await Promise.all([
        getDashboardOverview(),
        getSmileTrend('week'),
        getSmileForecast(12), // Get 12 hour forecast
        getEmotionDistribution(),
        getWorkers(),
        getAlerts(),
        getRecentActivity()
      ]);
      if (!overview) throw new Error('Backend connection failed');
      setOverviewData(overview);
      setTrendData(trend);
      setForecastData(forecast);
      setEmotionData(emotion);
      setWorkersData(workers);
      setAlertsData(alerts);
      setActivityData(activity);
      setLastUpdated(new Date());
    } catch {
      setError('Unable to load dashboard data. Please check the backend connection.');
    } finally {
      setLoadingData(false);
    }
  }, []);

  // WebSocket connection with automatic reconnect
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    try {
      const ws = new WebSocket(`${WS_URL}/ws/dashboard`);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          // Refresh relevant data section based on event type
          if (msg.type === 'emotion_update' || msg.type === 'new_alert') {
            fetchDashboardData();
          }
        } catch {}
      };

      ws.onclose = () => {
        setWsConnected(false);
        // Reconnect after 5 seconds
        reconnectTimer.current = setTimeout(connectWebSocket, 5000);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      // WebSocket not available; fall back to polling silently
    }
  }, [fetchDashboardData]);

  useEffect(() => {
    if (!session) return;

    fetchDashboardData();
    connectWebSocket();

    // Fallback polling every 30s in case WebSocket is unavailable
    const interval = setInterval(fetchDashboardData, 30000);

    return () => {
      clearInterval(interval);
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [session, fetchDashboardData, connectWebSocket]);

  if (loadingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Workforce Overview</h2>
            {lastUpdated && (
              <p className="text-xs text-gray-400 mt-0.5">
                Updated {lastUpdated.toLocaleTimeString('en-IN')}
              </p>
            )}
          </div>
          <div className="flex items-center space-x-3">
            {/* WebSocket status indicator */}
            <div className={`flex items-center space-x-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${wsConnected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
              {wsConnected
                ? <><Wifi className="w-3.5 h-3.5" /><span>Live</span></>
                : <><WifiOff className="w-3.5 h-3.5" /><span>Polling</span></>
              }
            </div>
            <button
              onClick={fetchDashboardData}
              disabled={loadingData}
              className="flex items-center space-x-2 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-blue-600 hover:bg-blue-50 bg-white border border-gray-200 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loadingData ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
              <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}

          <KPIOverview data={overviewData} />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <SmileTrendChart data={trendData} forecast={forecastData} />
            </div>
            <div>
              <EmotionDistribution data={emotionData} />
            </div>
          </div>

          {/* Production Risk History + Department Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ProductionRiskHistory />
            <DepartmentOverview />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <WorkerStatus data={workersData} />
            </div>
            <div className="space-y-6">
              <AlertsPanel data={alertsData} />
              <RecentActivity data={activityData} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
