/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from 'react';
import { Device } from '@/lib/deviceApi';
import { Factory } from '@/lib/factoryApi';
import { X, Loader2 } from 'lucide-react';

interface DeviceFormProps {
  device?: Device | null;
  factories: Factory[];
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Device>) => Promise<void>;
}

export function DeviceForm({ device, factories, isOpen, onClose, onSubmit }: DeviceFormProps) {
  const [formData, setFormData] = useState<Partial<Device>>({
    device_name: '',
    device_type: 'esp32',
    factory_id: '',
    mac_address: '',
    location: '',
    firmware_version: '',
    description: '',
    status: 'inactive',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      if (device) {
        setFormData({
          device_name: device.device_name,
          device_type: device.device_type,
          factory_id: device.factory_id || '',
          mac_address: device.mac_address || '',
          location: device.location || '',
          firmware_version: device.firmware_version || '',
          description: device.description || '',
          status: device.status,
        });
      } else {
        setFormData({
          device_name: '',
          device_type: 'esp32',
          factory_id: '',
          mac_address: '',
          location: '',
          firmware_version: '',
          description: '',
          status: 'inactive',
        });
      }
      setError('');
    }
  }, [isOpen, device]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    const submitData = { ...formData };
    if (!submitData.mac_address) delete submitData.mac_address;
    if (!submitData.factory_id) delete submitData.factory_id;
    if (!submitData.location) delete submitData.location;
    if (!submitData.firmware_version) delete submitData.firmware_version;
    if (!submitData.description) delete submitData.description;

    try {
      await onSubmit(submitData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'An error occurred while saving the device');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">
            {device ? 'Edit Device' : 'Add Device'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          {device && (
            <div className="mb-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-700 flex justify-between">
              <span className="font-medium">Device Code</span>
              <span className="font-mono font-bold">{device.device_code}</span>
            </div>
          )}

          <form id="device-form" onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Device Name *</label>
              <input
                type="text"
                required
                value={formData.device_name}
                onChange={(e) => setFormData({ ...formData, device_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Device Type *</label>
                <select
                  required
                  value={formData.device_type}
                  onChange={(e) => setFormData({ ...formData, device_type: e.target.value as any })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                >
                  <option value="esp32">ESP32</option>
                  <option value="rfid_reader">RFID Reader</option>
                  <option value="button_panel">Button Panel</option>
                  <option value="camera">Camera</option>
                  <option value="gateway">Gateway</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">MAC Address</label>
                <input
                  type="text"
                  value={formData.mac_address || ''}
                  onChange={(e) => setFormData({ ...formData, mac_address: e.target.value.trim().toUpperCase() })}
                  placeholder="e.g. AA:BB:CC:DD:EE:FF"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Factory</label>
                <select
                  value={formData.factory_id || ''}
                  onChange={(e) => setFormData({ ...formData, factory_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                >
                  <option value="">[ Select Factory ]</option>
                  {factories.map((f) => (
                    <option key={f.factory_id} value={f.factory_id}>
                      {f.factory_name}
                    </option>
                  ))}
                </select>
                {factories.length === 0 && (
                  <p className="mt-1 text-xs text-amber-600">No factories available. Please create a factory first.</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location / Area</label>
                <input
                  type="text"
                  value={formData.location || ''}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="e.g. Production Line 1"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Firmware Version</label>
                <input
                  type="text"
                  value={formData.firmware_version || ''}
                  onChange={(e) => setFormData({ ...formData, firmware_version: e.target.value })}
                  placeholder="e.g. 1.0.0"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                  disabled={!device} // Only editable on update. Creation should default to inactive
                >
                  <option value="inactive">Inactive</option>
                  <option value="online">Online</option>
                  <option value="offline">Offline</option>
                  <option value="maintenance">Maintenance</option>
                </select>
                {!device && <p className="mt-1 text-xs text-gray-500">Newly created devices default to Inactive.</p>}
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none resize-none"
              />
            </div>
          </form>
        </div>

        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="device-form"
            disabled={loading || (factories.length === 0)}
            className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
            {device ? 'Save Changes' : 'Create Device'}
          </button>
        </div>
      </div>
    </div>
  );
}
