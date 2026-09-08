"use client";

import { useState, useEffect } from 'react';
import { getReportLogs } from '@/../lib/reportsApi';
import { getFactories } from '../../lib/factoryApi';
import Navbar from '@/components/Navbar';
import { Download, AlertTriangle, FileText } from 'lucide-react';

export default function ReportsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [factories, setFactories] = useState<any[]>([]);
  const [selectedFactory, setSelectedFactory] = useState<string>('');
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    // Fetch factories on mount
    const fetchFacs = async () => {
      try {
        const facs = await getFactories();
        setFactories(facs?.data || facs || []);
      } catch (err) {
        console.error("Failed to load factories", err);
      }
    };
    fetchFacs();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    try {
      // Always use today for the "report of the day"
      const start = new Date();
      start.setHours(0,0,0,0);
      const end = new Date();
      
      const filters = { 
        start_date: start.toISOString(), 
        end_date: end.toISOString(),
        factory_id: selectedFactory || undefined
      };
      
      const res = await getReportLogs(filters);
      setLogs(res.logs || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load report data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [selectedFactory]);

  const downloadPdf = () => {
    // In a real app, this would use jsPDF or html2pdf to generate a PDF,
    // or trigger a backend endpoint that returns a PDF.
    // For now, we'll trigger the browser's print dialog.
    window.print();
  };

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
      <div className="p-6 md:p-8 max-w-screen-xl mx-auto space-y-6 pb-20">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <FileText className="h-6 w-6 text-blue-600" />
              Daily Mood Report
            </h1>
            <p className="text-gray-500 mt-1 text-sm">View today's worker mood logs by factory.</p>
          </div>
          
          <div className="flex flex-wrap items-center gap-3">
            <select 
              className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[200px]"
              value={selectedFactory}
              onChange={(e) => setSelectedFactory(e.target.value)}
            >
              <option value="">All Factories</option>
              {factories.map(f => (
                <option key={f.factory_id} value={f.factory_id}>{f.factory_name}</option>
              ))}
            </select>
            <button 
              onClick={downloadPdf} 
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors shadow-sm font-medium"
            >
              <Download className="h-4 w-4" /> Download PDF
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          {loading ? (
            <div className="p-12 flex justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="overflow-x-auto print:overflow-visible">
              <table className="w-full text-sm text-left">
                <thead className="bg-gray-50 text-gray-500 uppercase text-xs font-semibold">
                  <tr>
                    <th className="px-6 py-4">Worker ID</th>
                    <th className="px-6 py-4">Worker Name</th>
                    <th className="px-6 py-4">Mood</th>
                    <th className="px-6 py-4">Department</th>
                    <th className="px-6 py-4">Factory</th>
                    <th className="px-6 py-4">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {logs.map((log, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-medium text-gray-900">{log.worker_id}</td>
                      <td className="px-6 py-4">{log.worker_name}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium uppercase tracking-wide ${
                          log.mood === 'happy' ? 'bg-green-100 text-green-700' :
                          log.mood === 'sad' ? 'bg-red-100 text-red-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>
                          {log.mood}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{log.department}</td>
                      <td className="px-6 py-4 text-gray-600">{log.factory}</td>
                      <td className="px-6 py-4 text-gray-500 text-xs">
                        {new Date(log.recorded_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </td>
                    </tr>
                  ))}
                  {logs.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center">
                        <p className="text-gray-500 font-medium">No mood logs recorded today.</p>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
