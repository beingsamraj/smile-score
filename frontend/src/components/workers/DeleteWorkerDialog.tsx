import { Worker } from '@/lib/workerApi';
import { X, AlertTriangle } from 'lucide-react';

interface DeleteWorkerDialogProps {
  worker: Worker | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function DeleteWorkerDialog({ worker, isOpen, onClose, onConfirm }: DeleteWorkerDialogProps) {
  if (!isOpen || !worker) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">Deactivate Worker</h2>
          <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-gray-700">Are you sure you want to deactivate <span className="font-semibold">{worker.name}</span>?</p>
              <p className="text-sm text-gray-500 mt-2">This will mark the worker as inactive. Their data will not be deleted.</p>
            </div>
          </div>
        </div>
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3">
          <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Cancel
          </button>
          <button type="button" onClick={() => { onConfirm(); onClose(); }} className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors">
            Deactivate
          </button>
        </div>
      </div>
    </div>
  );
}
