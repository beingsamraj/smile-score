import { Device } from '@/lib/deviceApi';
import { Edit, Trash2, Eye, Server, Radio, ZapOff, Settings } from 'lucide-react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';

interface DeviceTableProps {
  devices: Device[];
  onEdit: (device: Device) => void;
  onDelete: (device: Device) => void;
}

export function DeviceTable({ devices, onEdit, onDelete }: DeviceTableProps) {
  if (devices.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
        <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <Server className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">No devices found</h3>
        <p className="text-gray-500">No IoT devices have been registered yet.</p>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'online':
        return <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200"><Radio className="w-3 h-3 mr-1" /> Online</span>;
      case 'offline':
        return <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200"><ZapOff className="w-3 h-3 mr-1" /> Offline</span>;
      case 'maintenance':
        return <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200"><Settings className="w-3 h-3 mr-1 animate-spin-slow" /> Maint.</span>;
      default:
        return <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200">Inactive</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-gray-50 border-b border-gray-100 text-gray-600">
            <tr>
              <th className="px-6 py-4 font-medium">Device Code</th>
              <th className="px-6 py-4 font-medium">Device Name</th>
              <th className="px-6 py-4 font-medium">Type</th>
              <th className="px-6 py-4 font-medium">Location</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Last Seen</th>
              <th className="px-6 py-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {devices.map((device) => (
              <tr key={device.id} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-4 font-medium text-gray-900 font-mono text-xs">
                  {device.device_code}
                </td>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{device.device_name}</div>
                  {device.mac_address && <div className="text-gray-400 font-mono text-xs mt-0.5">{device.mac_address}</div>}
                </td>
                <td className="px-6 py-4">
                  <span className="capitalize text-gray-700">{device.device_type.replace('_', ' ')}</span>
                </td>
                <td className="px-6 py-4 text-gray-600">
                  <div className="font-medium">{device.factory_name || '-'}</div>
                  {device.location && <div className="text-gray-500 text-xs mt-0.5">{device.location}</div>}
                </td>
                <td className="px-6 py-4">
                  {getStatusBadge(device.status)}
                </td>
                <td className="px-6 py-4 text-gray-500 text-xs">
                  {device.last_seen ? formatDistanceToNow(new Date(device.last_seen), { addSuffix: true }) : 'Never'}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <Link
                      href={`/devices/${device.id}`}
                      className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4" />
                    </Link>
                    <button
                      onClick={() => onEdit(device)}
                      className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Edit Device"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onDelete(device)}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete/Deactivate"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
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
