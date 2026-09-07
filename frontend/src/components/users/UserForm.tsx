/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from 'react';
import { User } from '@/lib/userApi';
import { Factory } from '@/lib/factoryApi';
import { X, Loader2 } from 'lucide-react';

interface UserFormProps {
  user?: User | null;
  factories: Factory[];
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<User>) => Promise<void>;
}

export function UserForm({ user, factories, isOpen, onClose, onSubmit }: UserFormProps) {
  const [formData, setFormData] = useState<Partial<User>>({
    full_name: '',
    email: '',
    phone: '',
    role: 'worker',
    factory_id: '',
    rfid_uid: '',
    status: 'active',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      if (user) {
        setFormData({
          full_name: user.full_name,
          email: user.email || '',
          phone: user.phone || '',
          role: user.role,
          factory_id: user.factory_id || '',
          rfid_uid: user.rfid_uid || '',
          status: user.status,
        });
      } else {
        setFormData({
          full_name: '',
          email: '',
          phone: '',
          role: 'worker',
          factory_id: '',
          rfid_uid: '',
          status: 'active',
        });
      }
      setError('');
    }
  }, [isOpen, user]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    // Clean up empty strings to nulls for optional unique fields
    const submitData = { ...formData };
    if (!submitData.email) delete submitData.email;
    if (!submitData.phone) delete submitData.phone;
    if (!submitData.rfid_uid) delete submitData.rfid_uid;
    if (!submitData.factory_id) delete submitData.factory_id;

    try {
      await onSubmit(submitData);
      onClose();
    } catch (err: any) {
      setError(err.message || 'An error occurred while saving the user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">
            {user ? 'Edit User' : 'Add User'}
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
          
          {user && (
            <div className="mb-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-700 flex justify-between">
              <span className="font-medium">Employee Code</span>
              <span className="font-mono font-bold">{user.employee_code}</span>
            </div>
          )}

          <form id="user-form" onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
              <input
                type="text"
                required
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={formData.email || ''}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={formData.phone || ''}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role *</label>
                <select
                  required
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                >
                  <option value="worker">Worker</option>
                  <option value="supervisor">Supervisor</option>
                  <option value="manager">Manager</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status *</label>
                <select
                  required
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
            </div>

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
              <label className="block text-sm font-medium text-gray-700 mb-1">RFID UID</label>
              <input
                type="text"
                value={formData.rfid_uid || ''}
                onChange={(e) => setFormData({ ...formData, rfid_uid: e.target.value.trim().toUpperCase() })}
                placeholder="e.g. A39F217B"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none font-mono"
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
            form="user-form"
            disabled={loading}
            className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
            {user ? 'Save Changes' : 'Create User'}
          </button>
        </div>
      </div>
    </div>
  );
}
