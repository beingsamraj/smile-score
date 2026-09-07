import { Worker } from '@/lib/workerApi';
import { Edit, Trash2 } from 'lucide-react';

interface WorkerTableProps {
  workers: Worker[];
  onEdit: (worker: Worker) => void;
  onDelete: (worker: Worker) => void;
}

export function WorkerTable({ workers, onEdit, onDelete }: WorkerTableProps) {
  if (workers.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-1">No workers found</h3>
        <p className="text-gray-500">No workers have been registered yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-gray-50 border-b border-gray-100 text-gray-600">
            <tr>
              <th className="px-6 py-4 font-medium">Employee ID</th>
              <th className="px-6 py-4 font-medium">Name</th>
              <th className="px-6 py-4 font-medium">Factory</th>
              <th className="px-6 py-4 font-medium">Department</th>
              <th className="px-6 py-4 font-medium">Designation</th>
              <th className="px-6 py-4 font-medium">RFID</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Created Date</th>
              <th className="px-6 py-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {workers.map((worker) => (
              <tr key={worker.worker_id} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-4 font-medium text-gray-900">{worker.employee_id}</td>
                <td className="px-6 py-4"><div className="font-medium text-gray-900">{worker.name}</div></td>
                <td className="px-6 py-4 text-gray-600">{worker.factory_name || '-'}</td>
                <td className="px-6 py-4 text-gray-600">{worker.department_name || '-'}</td>
                <td className="px-6 py-4"><span className="capitalize text-gray-700">{worker.designation || '-'}</span></td>
                <td className="px-6 py-4 text-gray-600 font-mono text-xs">{worker.rfid_uid ? worker.rfid_uid : 'Not Assigned'}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${worker.status ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                    {worker.status ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-500">{new Date(worker.created_at).toLocaleDateString()}</td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button onClick={() => onEdit(worker)} className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="Edit Worker"><Edit className="w-4 h-4" /></button>
                    <button onClick={() => onDelete(worker)} className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Delete Worker"><Trash2 className="w-4 h-4" /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
