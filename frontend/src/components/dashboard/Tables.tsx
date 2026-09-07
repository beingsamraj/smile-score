/* eslint-disable @typescript-eslint/no-explicit-any */
export function WorkerStatus({ data }: { data: any }) {
  if (!data) return <div className="p-4 bg-white rounded-xl border">Loading workers...</div>;
  if (!data.workers || data.workers.length === 0) return <div className="p-4 bg-white rounded-xl border text-gray-500">No worker data available</div>;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-800">Worker Status</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-600 font-medium">
            <tr>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {data.workers.map((w: any) => (
              <tr key={w.id} className="border-b border-gray-50 last:border-0 hover:bg-gray-50">
                <td className="px-4 py-3">{w.worker_code}</td>
                <td className="px-4 py-3 font-medium">{w.name}</td>
                <td className="px-4 py-3">{w.department}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${w.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                    {w.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AlertsPanel({ data }: { data: any }) {
  if (!data) return <div className="p-4 bg-white rounded-xl border">Loading alerts...</div>;
  if (!data.alerts || data.alerts.length === 0) return <div className="p-4 bg-white rounded-xl border text-green-600 font-medium flex items-center">✓ No active alerts</div>;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 bg-red-50">
        <h3 className="text-lg font-semibold text-red-800">Active Alerts</h3>
      </div>
      <div className="divide-y divide-gray-100">
        {data.alerts.map((alert: any) => (
          <div key={alert.id} className="p-4 flex flex-col">
            <div className="flex justify-between items-start mb-1">
              <span className={`text-xs font-bold px-2 py-1 rounded uppercase ${alert.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                {alert.severity}
              </span>
              <span className="text-xs text-gray-500">{new Date(alert.timestamp).toLocaleString()}</span>
            </div>
            <p className="text-sm text-gray-800 mt-1">{alert.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function RecentActivity({ data }: { data: any }) {
  if (!data) return <div className="p-4 bg-white rounded-xl border">Loading activity...</div>;
  if (!data.activities || data.activities.length === 0) return <div className="p-4 bg-white rounded-xl border text-gray-500">No recent activity</div>;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {data.activities.map((act: any, i: number) => (
          <div key={i} className="flex items-start">
            <div className="w-2 h-2 mt-1.5 rounded-full bg-blue-500 mr-3"></div>
            <div>
              <p className="text-sm font-medium text-gray-800">{act.worker} logged {act.event}</p>
              <p className="text-xs text-gray-500">{new Date(act.timestamp).toLocaleString()} • {act.device}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
