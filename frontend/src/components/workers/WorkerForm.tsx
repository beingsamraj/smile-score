/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback } from 'react';
import { Worker } from '@/lib/workerApi';
import { Factory } from '@/lib/factoryApi';
import { X, Save } from 'lucide-react';

interface Department {
  department_id: string;
  department_name: string;
  factory_id: string;
}

interface WorkerFormProps {
  worker: Worker | null;
  factories: Factory[];
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Worker>) => void;
}

export function WorkerForm({ worker, factories, isOpen, onClose, onSubmit }: WorkerFormProps) {
  const [formData, setFormData] = useState<Partial<Worker>>({
    name: '',
    factory_id: '',
    department_id: '',
    designation: '',
    rfid_uid: '',
    status: true,
  });

  const [departments, setDepartments] = useState<Department[]>([]);

  const fetchDepartments = useCallback(async (factoryId: string) => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${API_URL}/api/departments?factory_id=${factoryId}`);
      if (res.ok) {
        const data = await res.json();
        setDepartments(data.data || []);
      }
    } catch (e) {
      console.error('Error fetching departments', e);
    }
  }, []);

  useEffect(() => {
    if (!isOpen) return;
    if (worker) {
      setFormData({ ...worker });
      if (worker.factory_id) {
        fetchDepartments(worker.factory_id);
      }
    } else {
      setFormData({
        name: '',
        factory_id: '',
        department_id: '',
        designation: '',
        rfid_uid: '',
        status: true,
      });
      setDepartments([]);
    }
  }, [worker, isOpen, fetchDepartments]);

  const handleFactoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setFormData((prev) => ({ ...prev, factory_id: val, department_id: '' }));
    if (val) {
      fetchDepartments(val);
    } else {
      setDepartments([]);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">
            {worker ? 'Edit Worker' : 'Add New Worker'}
          </h2>
          <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={(e) => { e.preventDefault(); onSubmit(formData); onClose(); }} className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={formData.name || ''}
                onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Factory</label>
                <select
                  required
                  value={formData.factory_id || ''}
                  onChange={handleFactoryChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none bg-white"
                >
                  <option value="">Select Factory</option>
                  {factories.map(f => (
                    <option key={f.factory_id} value={f.factory_id}>{f.factory_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <select
                  required
                  value={formData.department_id || ''}
                  onChange={(e) => setFormData((prev) => ({ ...prev, department_id: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none bg-white"
                >
                  <option value="">Select Department</option>
                  {departments.map(d => (
                    <option key={d.department_id} value={d.department_id}>{d.department_name}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Designation</label>
                <input
                  type="text"
                  value={formData.designation || ''}
                  onChange={(e) => setFormData((prev) => ({ ...prev, designation: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={formData.status ? 'active' : 'inactive'}
                  onChange={(e) => setFormData((prev) => ({ ...prev, status: e.target.value === 'active' }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none bg-white"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">RFID UID</label>
              <input
                type="text"
                required
                value={formData.rfid_uid || ''}
                onChange={(e) => setFormData((prev) => ({ ...prev, rfid_uid: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                placeholder="e.g. A1B2C3D4"
              />
            </div>
          </div>

          <div className="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              Cancel
            </button>
            <button type="submit" className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
              <Save className="w-4 h-4 mr-2" />
              {worker ? 'Update Worker' : 'Save Worker'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
