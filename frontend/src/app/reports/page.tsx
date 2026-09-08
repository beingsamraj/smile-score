"use client";

import { useState, useEffect } from 'react';
import { 
  getReportSummary, getSmileScoreTrend, getEmotionDistribution, 
  getDepartmentsAnalysis, getWorkersAnalysis, getRiskAnalysis, getFactoriesAnalysis
} from '../../../lib/reportsApi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Calendar, Filter, Download, Activity, AlertTriangle, Users, Smile, Meh, Frown, Factory, Building, Search } from 'lucide-react';
import Image from 'next/image';
import Navbar from '@/components/Navbar';

const EMOTION_COLORS = {
  happy: '#10B981', // green
  ok: '#F59E0B',    // yellow
  sad: '#EF4444'    // red
};

export default function ReportsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [dateRange, setDateRange] = useState('30days');
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');
  
  // Data state
  const [summary, setSummary] = useState<any>(null);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [emotionData, setEmotionData] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [factories, setFactories] = useState<any[]>([]);
  const [workers, setWorkers] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    try {
      let start_date = '';
      let end_date = '';
      
      if (dateRange !== 'custom') {
        const now = new Date();
        end_date = now.toISOString();
        const start = new Date();
        
        if (dateRange === 'today') start.setHours(0,0,0,0);
        else if (dateRange === '7days') start.setDate(now.getDate() - 7);
        else if (dateRange === '30days') start.setDate(now.getDate() - 30);
        else if (dateRange === 'thisMonth') {
          start.setDate(1);
          start.setHours(0,0,0,0);
        }
        
        start_date = start.toISOString();
      } else {
        start_date = customStart ? new Date(customStart).toISOString() : '';
        end_date = customEnd ? new Date(customEnd).toISOString() : '';
      }
      
      const filters = { start_date, end_date };
      
      const [sum, trend, dist, deps, facs, wrks, risk] = await Promise.all([
        getReportSummary(filters),
        getSmileScoreTrend({...filters, aggregation: dateRange === 'today' ? 'hourly' : 'daily'}),
        getEmotionDistribution(filters),
        getDepartmentsAnalysis(filters),
        getFactoriesAnalysis(filters),
        getWorkersAnalysis(filters),
        getRiskAnalysis(filters)
      ]);
      
      setSummary(sum);
      setTrendData(trend.trend || []);
      
      if (dist) {
        setEmotionData([
          { name: 'Happy', value: dist.happy, color: EMOTION_COLORS.happy },
          { name: 'OK', value: dist.ok, color: EMOTION_COLORS.ok },
          { name: 'Sad', value: dist.sad, color: EMOTION_COLORS.sad }
        ]);
      }
      
      setDepartments(deps.departments || []);
      setFactories(facs.factories || []);
      setWorkers(wrks.workers || []);
      setAlerts(risk.alerts || []);
      
    } catch (err: any) {
      setError(err.message || 'Failed to load report data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [dateRange, customStart, customEnd]);

  if (loading && !summary) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="p-8 space-y-6 max-w-7xl mx-auto animate-pulse">
          <div className="h-10 w-64 bg-gray-200 rounded"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>)}
          </div>
          <div className="h-96 bg-gray-200 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="p-8 max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[60vh] text-center">
          <AlertTriangle className="h-16 w-16 text-red-500 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to load reports</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button onClick={fetchReports} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="p-6 md:p-8 max-w-screen-2xl mx-auto space-y-8 pb-20">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Workforce Wellbeing Reports</h1>
          <p className="text-gray-500 mt-1">Analyze worker happiness, wellbeing trends, and production risk indicators.</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select 
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
          >
            <option value="today">Today</option>
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
            <option value="thisMonth">This Month</option>
            <option value="custom">Custom Range</option>
          </select>
          <button onClick={() => window.print()} className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors shadow-sm">
            <Download className="h-4 w-4" /> Export PDF
          </button>
        </div>
      </div>

      {!summary?.has_data ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-16 flex flex-col items-center justify-center text-center">
          <Activity className="h-16 w-16 text-gray-300 mb-4" />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">No wellbeing data available</h3>
          <p className="text-gray-500 max-w-md">There is no feedback data recorded for the selected period. Try changing the date range or check if devices are online.</p>
        </div>
      ) : (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Activity className="h-5 w-5" /></div>
                <h3 className="text-gray-500 text-sm font-medium">Avg Smile Score</h3>
              </div>
              <div className="text-4xl font-bold text-gray-900 mt-4">{summary.average_smile_score}%</div>
            </div>
            
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg"><Smile className="h-5 w-5" /></div>
                <h3 className="text-gray-500 text-sm font-medium">Happy Responses</h3>
              </div>
              <div className="flex items-end gap-3 mt-4">
                <div className="text-4xl font-bold text-gray-900">{summary.happy_percentage}%</div>
                <div className="text-sm text-gray-500 mb-1">({summary.happy_count} total)</div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-red-50 text-red-600 rounded-lg"><Frown className="h-5 w-5" /></div>
                <h3 className="text-gray-500 text-sm font-medium">Sad Responses</h3>
              </div>
              <div className="flex items-end gap-3 mt-4">
                <div className="text-4xl font-bold text-gray-900">{summary.sad_percentage}%</div>
                <div className="text-sm text-gray-500 mb-1">({summary.sad_count} total)</div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-purple-50 text-purple-600 rounded-lg"><Users className="h-5 w-5" /></div>
                <h3 className="text-gray-500 text-sm font-medium">Active Workers</h3>
              </div>
              <div className="flex items-end gap-3 mt-4">
                <div className="text-4xl font-bold text-gray-900">{summary.active_workers}</div>
                <div className="text-sm text-gray-500 mb-1">({summary.at_risk_workers} at-risk)</div>
              </div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Smile Score Trend</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dx={-10} domain={[0, 100]} />
                    <RechartsTooltip 
                      contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}}
                      labelStyle={{fontWeight: 'bold', color: '#111827'}}
                    />
                    <Line type="monotone" dataKey="average_score" name="Avg Score" stroke="#3B82F6" strokeWidth={3} dot={{r: 4, fill: '#3B82F6', strokeWidth: 0}} activeDot={{r: 6}} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Emotion Distribution</h3>
              <div className="h-64 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={emotionData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {emotionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-3xl font-bold text-gray-900">{summary.total_responses}</span>
                  <span className="text-xs text-gray-500 font-medium uppercase tracking-wider">Total</span>
                </div>
              </div>
            </div>
          </div>

          {/* Risk Analysis */}
          {alerts.length > 0 && (
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                Workforce Risk Analysis
              </h3>
              <div className="space-y-4">
                {alerts.map((alert, idx) => (
                  <div key={idx} className={`p-4 rounded-xl border ${alert.severity === 'High Risk' ? 'bg-red-50 border-red-100' : 'bg-orange-50 border-orange-100'}`}>
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-xs font-bold px-2 py-1 rounded-md uppercase tracking-wide ${alert.severity === 'High Risk' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                            {alert.severity}
                          </span>
                          <span className="font-semibold text-gray-900">{alert.entity_name} ({alert.entity_type})</span>
                        </div>
                        <p className="text-gray-700 font-medium mt-2">{alert.type}: {alert.description}</p>
                        <p className="text-gray-500 text-sm mt-1">Recommended: {alert.recommended_action}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-gray-900">{alert.current_score}%</div>
                        <div className="text-xs text-gray-500">Current Score</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tables Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Departments Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900">Department Wellbeing</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="bg-gray-50 text-gray-500 uppercase text-xs font-semibold">
                    <tr>
                      <th className="px-6 py-4">Department</th>
                      <th className="px-6 py-4">Smile Score</th>
                      <th className="px-6 py-4">Happy %</th>
                      <th className="px-6 py-4">Risk Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {departments.map((dept, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">{dept.department_name}</td>
                        <td className="px-6 py-4">
                          <span className={`font-semibold ${dept.average_smile_score > 75 ? 'text-green-600' : dept.average_smile_score < 60 ? 'text-red-600' : 'text-orange-600'}`}>
                            {dept.average_smile_score}%
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">{dept.happy_percentage}%</td>
                        <td className="px-6 py-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                            dept.risk_status === 'Healthy' ? 'bg-green-100 text-green-700' :
                            dept.risk_status === 'High Risk' ? 'bg-red-100 text-red-700' :
                            'bg-orange-100 text-orange-700'
                          }`}>
                            {dept.risk_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {departments.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-6 py-8 text-center text-gray-500">No department data found.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Workers Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900">Worker Analysis</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="bg-gray-50 text-gray-500 uppercase text-xs font-semibold">
                    <tr>
                      <th className="px-6 py-4">Worker</th>
                      <th className="px-6 py-4">Dept</th>
                      <th className="px-6 py-4">Smile Score</th>
                      <th className="px-6 py-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {workers.slice(0, 10).map((worker, idx) => (
                      <tr key={idx} className="hover:bg-gray-50 cursor-pointer">
                        <td className="px-6 py-4">
                          <div className="font-medium text-gray-900">{worker.name}</div>
                          <div className="text-xs text-gray-500">{worker.employee_id}</div>
                        </td>
                        <td className="px-6 py-4 text-gray-600">{worker.department_name}</td>
                        <td className="px-6 py-4">
                          <span className={`font-semibold ${worker.average_smile_score > 75 ? 'text-green-600' : worker.average_smile_score < 60 ? 'text-red-600' : 'text-orange-600'}`}>
                            {worker.average_smile_score}%
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                            worker.status === 'Excellent' || worker.status === 'Good' ? 'bg-green-100 text-green-700' :
                            worker.status === 'High Risk' ? 'bg-red-100 text-red-700' :
                            worker.status === 'Stable' ? 'bg-blue-100 text-blue-700' :
                            'bg-orange-100 text-orange-700'
                          }`}>
                            {worker.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {workers.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-6 py-8 text-center text-gray-500">No worker data found.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
              {workers.length > 10 && (
                <div className="p-4 border-t border-gray-100 text-center bg-gray-50">
                  <span className="text-sm text-blue-600 font-medium cursor-pointer hover:underline">View all {workers.length} workers</span>
                </div>
              )}
            </div>

          </div>
        </>
      )}
      </div>
    </div>
  );
}
