/* eslint-disable @typescript-eslint/no-explicit-any */
import { User } from '@/lib/userApi';
import { X, AlertTriangle, Loader2 } from 'lucide-react';
import { useState } from 'react';

interface DeleteUserDialogProps {
  user: User | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

export function DeleteUserDialog({ user, isOpen, onClose, onConfirm }: DeleteUserDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen || !user) return null;

  const handleConfirm = async () => {
    setError('');
    setLoading(true);
    try {
      await onConfirm();
      onClose();
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            Deactivate User?
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <p className="text-gray-600 mb-4">
            Are you sure you want to deactivate this user? Historical worker data may depend on this user.
          </p>

          <div className="bg-gray-50 rounded-lg p-4 space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-500 text-sm">Employee Code</span>
              <span className="font-medium text-gray-900 font-mono">{user.employee_code}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500 text-sm">Name</span>
              <span className="font-medium text-gray-900">{user.full_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500 text-sm">Role</span>
              <span className="font-medium text-gray-900 capitalize">{user.role}</span>
            </div>
          </div>
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
            type="button"
            onClick={handleConfirm}
            disabled={loading}
            className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
            Deactivate
          </button>
        </div>
      </div>
    </div>
  );
}
