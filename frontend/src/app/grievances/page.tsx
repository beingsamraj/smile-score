"use client";

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import { 
  getGrievanceMetrics, 
  getGrievances, 
  triggerGrievanceDetection,
  GrievanceMetrics,
  GrievanceRecord
} from '@/lib/grievanceApi';

import { RefreshCw, Filter, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import GrievanceDetailModal from '@/components/grievances/GrievanceDetailModal';

export default function GrievancesPage() {
  const [metrics, setMetrics] = useState<GrievanceMetrics | null>(null);
  const [records, setRecords] = useState<GrievanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [departments, setDepartments] = useState<any[]>([]); // eslint-disable-line @typescript-eslint/no-explicit-any
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [deptFilter, setDeptFilter] = useState('ALL');
  const [dateFilter, setDateFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  
  // Detail Modal
  const [selectedGrievanceId, setSelectedGrievanceId] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [mRes, gRes, dRes] = await Promise.all([
        getGrievanceMetrics(),
        getGrievances(page, 20, statusFilter, deptFilter, dateFilter),
        fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/dashboard/departments').then(r => r.json()).catch(() => [])
      ]);
      setMetrics(mRes);
      setRecords(gRes.data);
      setTotal(gRes.total);
      setDepartments(dRes.data || dRes || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(); // eslint-disable-line
    // eslint-disable-next-line react-hooks/exhaustive-deps, react-hooks/set-state-in-effect
  }, [page, statusFilter, deptFilter, dateFilter]);

  const handleDetect = async () => {
    try {
      await triggerGrievanceDetection();
      fetchData(); // eslint-disable-line
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Wellbeing Grievances</h1>
            <p className="text-sm text-gray-500 mt-1">Identify and manage repeated wellbeing concerns</p>
          </div>
          <button 
            onClick={handleDetect}
            className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md shadow-sm transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Run Detection</span>
          </button>
        </div>

        {/* Metrics Cards */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="text-sm font-medium text-gray-500 mb-1">Total Grievances</div>
              <div className="text-3xl font-bold text-gray-900">{metrics.TOTAL}</div>
            </div>
            <div className="bg-red-50 p-6 rounded-xl shadow-sm border border-red-100">
              <div className="flex items-center text-sm font-medium text-red-600 mb-1">
                <AlertTriangle className="w-4 h-4 mr-1" /> New
              </div>
              <div className="text-3xl font-bold text-red-700">{metrics.NEW}</div>
            </div>
            <div className="bg-yellow-50 p-6 rounded-xl shadow-sm border border-yellow-100">
              <div className="flex items-center text-sm font-medium text-yellow-600 mb-1">
                <Clock className="w-4 h-4 mr-1" /> Under Review
              </div>
              <div className="text-3xl font-bold text-yellow-700">{metrics["UNDER REVIEW"]}</div>
            </div>
            <div className="bg-green-50 p-6 rounded-xl shadow-sm border border-green-100">
              <div className="flex items-center text-sm font-medium text-green-600 mb-1">
                <CheckCircle className="w-4 h-4 mr-1" /> Resolved
              </div>
              <div className="text-3xl font-bold text-green-700">{metrics.RESOLVED}</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6 flex flex-col sm:flex-row gap-4 items-center">
          <div className="flex items-center w-full sm:w-auto">
            <Filter className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>
          
          <select 
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">New</option>
            <option value="UNDER REVIEW">Under Review</option>
            <option value="RESOLVED">Resolved</option>
          </select>

          <select 
            value={deptFilter}
            onChange={e => setDeptFilter(e.target.value)}
            className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
          >
            <option value="ALL">All Departments</option>
            {departments.map((d: any) /* eslint-disable-line @typescript-eslint/no-explicit-any */ => (
              <option key={d.id || d.name} value={d.name}>{d.name}</option>
            ))}
          </select>

          <div className="flex items-center space-x-2">
            <input 
              type="date"
              value={dateFilter === 'all' ? '' : dateFilter}
              onChange={e => setDateFilter(e.target.value || 'all')}
              className="block w-full sm:w-48 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
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

        {/* Table */}
        <div className="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trigger Reason</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">Loading...</td>
                  </tr>
                ) : records.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">No wellbeing grievances found matching filters.</td>
                  </tr>
                ) : (
                  records.map((record) => (
                    <tr key={record.grievance_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{record.employee_name}</div>
                        <div className="text-sm text-gray-500">{record.employee_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {record.department}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={record.trigger_reason}>
                        {record.trigger_reason}
                        <div className="text-xs text-gray-400 mt-1">Total SAD: {record.total_sad_count}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          record.risk_level === 'HIGH' ? 'bg-red-100 text-red-800' : 
                          record.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-green-100 text-green-800'
                        }`}>
                          {record.risk_level || 'UNKNOWN'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          record.grievance_status === 'NEW' ? 'bg-red-100 text-red-800' : 
                          record.grievance_status === 'UNDER REVIEW' ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-green-100 text-green-800'
                        }`}>
                          {record.grievance_status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button 
                          onClick={() => setSelectedGrievanceId(record.grievance_id)}
                          className="text-indigo-600 hover:text-indigo-900 bg-indigo-50 px-3 py-1 rounded-md"
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
          <div className="bg-white px-4 py-3 border-t border-gray-200 flex items-center justify-between sm:px-6">
            <div className="text-sm text-gray-700">
              Showing page {page} of {Math.ceil(total / 20) || 1}
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
        </div>

      </main>

      {/* Modal */}
      {selectedGrievanceId && (
        <GrievanceDetailModal 
          grievanceId={selectedGrievanceId} 
          onClose={() => setSelectedGrievanceId(null)} 
          onUpdated={fetchData} 
        />
      )}
    </div>
  );
}
