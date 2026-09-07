/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/set-state-in-effect */
'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, RefreshCw, AlertTriangle } from 'lucide-react';
import { getSession } from '@/../lib/auth';
import { 
  getDashboardOverview, getSmileTrend, getEmotionDistribution, 
  getWorkers, getAlerts, getRecentActivity
} from '@/../lib/dashboardApi';
import KPIOverview from '@/components/dashboard/KPIOverview';
import { SmileTrendChart, EmotionDistribution } from '@/components/dashboard/Charts';
import { WorkerStatus, AlertsPanel, RecentActivity } from '@/components/dashboard/Tables';
import Navbar from '@/components/Navbar';

export default function DashboardPage() {
  const router = useRouter();
  const [session, setSession] = useState<any>(null);
  const [loadingAuth, setLoadingAuth] = useState(true);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Dashboard Data State
  const [overviewData, setOverviewData] = useState<any>(null);
  const [trendData, setTrendData] = useState<any>(null);
  const [emotionData, setEmotionData] = useState<any>(null);
  const [workersData, setWorkersData] = useState<any>(null);
  const [alertsData, setAlertsData] = useState<any>(null);
  const [activityData, setActivityData] = useState<any>(null);

  useEffect(() => {
    async function checkAuth() {
      try {
        const { data, error } = await getSession();
        if (error || !data.session) {
          router.push('/login');
          return;
        }
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
      const [overview, trend, emotion, workers, alerts, activity] = await Promise.all([
        getDashboardOverview(),
        getSmileTrend('today'),
        getEmotionDistribution(),
        getWorkers(),
        getAlerts(),
        getRecentActivity()
      ]);
      
      if (!overview) throw new Error("Backend connection failed");

      setOverviewData(overview);
      setTrendData(trend);
      setEmotionData(emotion);
      setWorkersData(workers);
      setAlertsData(alerts);
      setActivityData(activity);
    } catch {
      setError('Unable to load dashboard data. Please check the backend connection.');
    } finally {
      setLoadingData(false);
    }
  }, []);

  useEffect(() => {
    if (session) {
      fetchDashboardData();
      const interval = setInterval(() => {
        fetchDashboardData();
      }, 30000); // 30 seconds refresh
      return () => clearInterval(interval);
    }
  }, [session, fetchDashboardData]);

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

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Workforce Overview</h2>
          <button 
            onClick={fetchDashboardData} 
            disabled={loadingData}
            className="flex items-center space-x-2 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-blue-600 hover:bg-blue-50 bg-white border border-gray-200 rounded-lg transition-colors disabled:opacity-50"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loadingData ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
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
              <SmileTrendChart data={trendData} />
            </div>
            <div>
              <EmotionDistribution data={emotionData} />
            </div>
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
