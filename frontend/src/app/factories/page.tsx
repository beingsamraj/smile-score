/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Search, Edit2, Trash2, X, AlertTriangle, Building2, Check, XCircle } from 'lucide-react';
import Navbar from '@/components/Navbar';
import { getSession } from '@/../lib/auth';
import { 
  getFactories, createFactory, updateFactory, deleteFactory, type Factory 
} from '@/lib/factoryApi';

export default function FactoriesPage() {
  const router = useRouter();
  const [loadingAuth, setLoadingAuth] = useState(true);
  const [loading, setLoading] = useState(true);
  const [factories, setFactories] = useState<Factory[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
  const [currentFactory, setCurrentFactory] = useState<Partial<Factory>>({});
  const [formLoading, setFormLoading] = useState(false);
  
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  useEffect(() => {
    async function checkAuth() {
      const { data } = await getSession();
      if (!data?.session) {
        router.push('/login');
        return;
      }
      setLoadingAuth(false);
    }
    checkAuth();
  }, [router]);

  const loadFactories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getFactories(searchTerm, statusFilter);
      setFactories(res.data || []);
    } catch {
      setError('Unable to load factories. Please check the backend connection and try again.');
    } finally {
      setLoading(false);
    }
  }, [searchTerm, statusFilter]);

  useEffect(() => {
    if (!loadingAuth) {
      const delay = setTimeout(() => {
        loadFactories();
      }, 300);
      return () => clearTimeout(delay);
    }
  }, [loadFactories, loadingAuth]);

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleOpenAddModal = () => {
    setModalMode('add');
    setCurrentFactory({ status: true });
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (factory: Factory) => {
    setModalMode('edit');
    setCurrentFactory(factory);
    setIsModalOpen(true);
  };

  const handleSaveFactory = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    try {
      // Clean numbers for empty values
      const dataToSave = { ...currentFactory };
      if (typeof dataToSave.no_of_employees === 'string' && dataToSave.no_of_employees === '') {
        dataToSave.no_of_employees = 0;
      }

      if (modalMode === 'add') {
        await createFactory(dataToSave);
        showToast('Factory created successfully.');
      } else {
        if (!currentFactory.factory_id) throw new Error("Missing ID");
        await updateFactory(currentFactory.factory_id, dataToSave);
        showToast('Factory updated successfully.');
      }
      setIsModalOpen(false);
      loadFactories();
    } catch (err: any) {
      showToast(err.message || 'Failed to save factory.', 'error');
    } finally {
      setFormLoading(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteConfirmId) return;
    setFormLoading(true);
    try {
      await deleteFactory(deleteConfirmId);
      showToast('Factory deleted successfully.');
      setDeleteConfirmId(null);
      loadFactories();
    } catch (err: any) {
      showToast(err.message || 'Failed to delete factory.', 'error');
      setDeleteConfirmId(null);
    } finally {
      setFormLoading(false);
    }
  };

  if (loadingAuth) {
    return <div className="min-h-screen flex items-center justify-center bg-gray-50">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <Navbar />
      
      {toast && (
        <div className={`fixed top-20 right-4 p-4 rounded shadow-lg z-50 flex items-center text-white ${toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'}`}>
          {toast.type === 'success' ? <Check className="w-5 h-5 mr-2" /> : <XCircle className="w-5 h-5 mr-2" />}
          {toast.message}
        </div>
      )}

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 space-y-4 md:space-y-0">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Building2 className="w-6 h-6 mr-3 text-blue-600" />
              Factories
            </h1>
            <p className="text-gray-500 mt-1">Manage factories and production locations</p>
          </div>
          <button 
            onClick={handleOpenAddModal}
            className="flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors shadow-sm"
          >
            <Plus className="w-5 h-5" />
            <span>Add Factory</span>
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6 flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input 
              type="text" 
              placeholder="Search factories..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-gray-900 bg-white"
            />
          </div>
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-gray-900 bg-white min-w-[150px]"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>

        {/* Content */}
        {error ? (
          <div className="bg-red-50 p-6 rounded-xl border border-red-200 flex flex-col items-center justify-center text-center">
            <AlertTriangle className="w-10 h-10 text-red-500 mb-3" />
            <h3 className="text-lg font-medium text-red-800">Connection Error</h3>
            <p className="text-red-600 mt-1 mb-4">{error}</p>
            <button onClick={loadFactories} className="px-4 py-2 bg-white text-red-700 border border-red-300 rounded-lg hover:bg-red-50 transition-colors">
              Retry
            </button>
          </div>
        ) : loading ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            Loading factories...
          </div>
        ) : factories.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center flex flex-col items-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Building2 className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-medium text-gray-900 mb-1">No factories found</h3>
            <p className="text-gray-500 mb-6">There are no factories registered yet or matching your search.</p>
            <button onClick={handleOpenAddModal} className="flex items-center space-x-2 text-blue-600 font-medium hover:text-blue-700">
              <Plus className="w-5 h-5" />
              <span>Add your first factory</span>
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-200 text-sm font-medium text-gray-600">
                    <th className="px-6 py-4 whitespace-nowrap">Factory Code</th>
                    <th className="px-6 py-4">Factory Name</th>
                    <th className="px-6 py-4">Address</th>
                    <th className="px-6 py-4">Employees</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {factories.map((factory) => (
                    <tr key={factory.factory_id} className="hover:bg-gray-50 transition-colors text-gray-800 text-sm">
                      <td className="px-6 py-4 font-medium">{factory.factory_id}</td>
                      <td className="px-6 py-4">{factory.factory_name}</td>
                      <td className="px-6 py-4">{factory.factory_address || '-'}</td>
                      <td className="px-6 py-4">{factory.no_of_employees || 0}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${
                          factory.status ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {factory.status ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right space-x-3 whitespace-nowrap">
                        <button 
                          onClick={() => handleOpenEditModal(factory)}
                          className="text-blue-600 hover:text-blue-900 inline-flex items-center"
                          title="Edit"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => setDeleteConfirmId(factory.factory_id)}
                          className="text-red-600 hover:text-red-900 inline-flex items-center"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* Add/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden flex flex-col max-h-[90vh]">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h3 className="text-lg font-bold text-gray-900">
                {modalMode === 'add' ? 'Add Factory' : 'Edit Factory'}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleSaveFactory} className="flex-1 overflow-y-auto p-6 space-y-4 text-gray-800">
              {modalMode === 'edit' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Factory Code</label>
                  <input 
                    type="text" 
                    value={currentFactory.factory_id || ''} 
                    disabled 
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed"
                  />
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Factory Name *</label>
                <input 
                  required
                  type="text" 
                  value={currentFactory.factory_name || ''} 
                  onChange={(e) => setCurrentFactory({...currentFactory, factory_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  placeholder="e.g. Main Production Plant"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Factory Address</label>
                <input 
                  type="text" 
                  value={currentFactory.factory_address || ''} 
                  onChange={(e) => setCurrentFactory({...currentFactory, factory_address: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Number of Employees</label>
                <input 
                  type="number" 
                  value={currentFactory.no_of_employees || ''} 
                  onChange={(e) => setCurrentFactory({...currentFactory, no_of_employees: parseInt(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select 
                  value={currentFactory.status ? 'active' : 'inactive'} 
                  onChange={(e) => setCurrentFactory({...currentFactory, status: e.target.value === 'active'})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-white"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>

              <div className="pt-4 flex items-center justify-end space-x-3 border-t border-gray-100 mt-6">
                <button 
                  type="button" 
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={formLoading}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {formLoading ? 'Saving...' : modalMode === 'add' ? 'Create Factory' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-sm overflow-hidden p-6 text-center text-gray-900">
            <div className="w-12 h-12 rounded-full bg-red-100 mx-auto flex items-center justify-center mb-4">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-lg font-bold mb-2">Delete Factory?</h3>
            <p className="text-gray-500 text-sm mb-6">
              Are you sure you want to delete this factory ({deleteConfirmId})? This action may not be possible if this factory has associated records.
            </p>
            <div className="flex space-x-3">
              <button 
                onClick={() => setDeleteConfirmId(null)}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-800 rounded-lg hover:bg-gray-200 font-medium transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={confirmDelete}
                disabled={formLoading}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors disabled:opacity-50"
              >
                {formLoading ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
