'use client';

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import { 
  getWellnessMetrics, 
  getWellness, 
  downloadWellnessReport,
  WellnessRecord
} from '@/lib/wellnessApi';
import WellnessDetailModal from '@/components/wellness/WellnessDetailModal';
import { Activity, Download, HeartPulse } from 'lucide-react';

export default function WellnessPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [records, setRecords] = useState<WellnessRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [departments, setDepartments] = useState<any[]>([]);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [deptFilter, setDeptFilter] = useState('ALL');
  const [dateFilter, setDateFilter] = useState('all');
  const [sortBy, setSortBy] = useState('detected_desc');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  
  // Detail Modal
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [mRes, wRes, dRes] = await Promise.all([
        getWellnessMetrics(),
        getWellness(page, 20, statusFilter, deptFilter, dateFilter, sortBy),
        fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/dashboard/departments').then(r => r.json()).catch(() => [])
      ]);
      setMetrics(mRes);
      setRecords(wRes.data);
      setTotal(wRes.total);
      setDepartments(dRes.data || dRes || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(); // eslint-disable-line
  }, [page, statusFilter, deptFilter, dateFilter, sortBy]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <HeartPulse className="w-6 h-6 mr-2 text-red-500" />
              Wellness & Medical Referrals
            </h1>
            <p className="text-sm text-gray-500 mt-1">Identify and manage employees requiring medical attention</p>
          </div>
          
          <button 
            onClick={downloadWellnessReport}
            className="mt-4 sm:mt-0 flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium text-sm transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Download Report
          </button>
        </div>

        {/* Metrics */}
        {metrics && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
              <div className="text-sm font-medium text-gray-500">Total Anomalies Detected</div>
              <div className="mt-2 text-3xl font-bold text-gray-900">{metrics.TOTAL}</div>
            </div>
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
              <div className="text-sm font-medium text-gray-500">Pending Nurse Reviews</div>
              <div className="mt-2 text-3xl font-bold text-orange-600">{records.filter(r => r.status === 'NEW').length}</div>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6 flex flex-wrap gap-4 items-center justify-between">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-700">Filters:</span>
            </div>
            
            <select 
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
            >
              <option value="ALL">All Statuses</option>
              <option value="NEW">New Alert</option>
              <option value="REFERRED TO NURSE">Referred to Nurse</option>
              <option value="TREATED">Treated</option>
              <option value="SENT TO HOSPITAL">Sent to Hospital</option>
            </select>

            <select 
              value={deptFilter}
              onChange={e => setDeptFilter(e.target.value)}
              className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
            >
              <option value="ALL">All Departments</option>
              {departments.map((d: any) => (
                <option key={d.id || d.name} value={d.name}>{d.name}</option>
              ))}
            </select>

            <div className="flex items-center space-x-2">
              <input 
                type="date"
                value={dateFilter === 'all' ? '' : dateFilter}
                onChange={e => setDateFilter(e.target.value || 'all')}
                className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
              />
              {dateFilter !== 'all' && (
                <button 
                  onClick={() => setDateFilter('all')}
                  className="text-xs text-gray-500 hover:text-gray-700 underline"
                >
                  Clear
                </button>
              )}
            </div>
          </div>
          
          <select 
            value={sortBy}
            onChange={e => setSortBy(e.target.value)}
            className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
          >
            <option value="detected_desc">Sort: Newest First</option>
            <option value="detected_asc">Sort: Oldest First</option>
            <option value="hr_desc">Sort: Highest Heart Rate</option>
            <option value="spo2_asc">Sort: Lowest SpO2</option>
          </select>
        </div>

        {/* Table */}
        <div className="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Vitals (Anomalous)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">AI Risk</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="relative px-6 py-3"><span className="sr-only">Action</span></th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">Loading...</td>
                  </tr>
                ) : records.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">No medical alerts found matching filters.</td>
                  </tr>
                ) : (
                  records.map((record, i) => (
                    <tr key={i} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-medium">{record.employee_name}</div>
                        <div className="text-sm text-gray-500">{record.employee_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{record.department}</div>
                        <div className="text-sm text-gray-500">{record.workstation}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 flex space-x-3">
                          <span className={record.avg_hr > 100 || record.avg_hr < 60 ? 'text-red-600 font-bold' : ''}>
                            HR: {Math.round(record.avg_hr)}
                          </span>
                          <span className={record.avg_spo2 < 95 ? 'text-red-600 font-bold' : ''}>
                            SpO2: {Math.round(record.avg_spo2)}%
                          </span>
                          <span className={record.avg_temp > 37.5 ? 'text-red-600 font-bold' : ''}>
                            Temp: {record.avg_temp.toFixed(1)}°
                          </span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">Alerts: {record.total_alerts}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          record.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                          record.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                          record.risk_level === 'MODERATE' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {record.risk_level || 'UNKNOWN'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          record.status === 'NEW' ? 'bg-red-50 text-red-700' : 
                          record.status === 'REFERRED TO NURSE' ? 'bg-orange-100 text-orange-800' :
                          record.status === 'TREATED' ? 'bg-green-100 text-green-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {record.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button 
                          onClick={() => setSelectedEmployeeId(record.employee_id)}
                          className="text-blue-600 hover:text-blue-900 bg-blue-50 px-3 py-1 rounded-md transition-colors"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          {/* Pagination */}
          {records.length > 0 && !loading && (
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Showing page {page} of {Math.ceil(total / 20) || 1} ({total} total)
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page * 20 >= total}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Modal */}
      {selectedEmployeeId && (
        <WellnessDetailModal 
          employeeId={selectedEmployeeId} 
          onClose={() => setSelectedEmployeeId(null)} 
          onUpdated={fetchData} 
        />
      )}
    </div>
  );
}
