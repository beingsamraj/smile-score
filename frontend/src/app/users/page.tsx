/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useState, useEffect, useCallback } from 'react';
import Navbar from '@/components/Navbar';
import { User, getUsers, createUser, updateUser, deleteUser } from '@/lib/userApi';
import { Factory, getFactories } from '@/lib/factoryApi';
import { UserTable } from '@/components/users/UserTable';
import { UserForm } from '@/components/users/UserForm';
import { DeleteUserDialog } from '@/components/users/DeleteUserDialog';
import { Plus, Search, Filter, Loader2, AlertCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { getSession } from '@/../lib/auth';

export default function UsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [factories, setFactories] = useState<Factory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [search, setSearch] = useState('');
  const [factoryFilter, setFactoryFilter] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  
  // Modals
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);

  const checkAuth = useCallback(async () => {
    const { data } = await getSession();
    if (!data.session) {
      router.push('/login');
      return false;
    }
    return true;
  }, [router]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      
      const [usersRes, factoriesRes] = await Promise.all([
        getUsers(search, factoryFilter, roleFilter, statusFilter, 1, 100),
        getFactories()
      ]);
      
      setUsers(usersRes.data || []);
      setFactories(factoriesRes.data || []);
    } catch (err: any) {
      setError(err.message || 'Unable to load users. Please check the backend connection.');
    } finally {
      setLoading(false);
    }
  }, [search, factoryFilter, roleFilter, statusFilter]);

  useEffect(() => {
    const init = async () => {
      const isAuth = await checkAuth();
      if (isAuth) {
        loadData();
      }
    };
    init();
  }, [checkAuth, loadData]);

  const handleAddClick = () => {
    setEditingUser(null);
    setIsFormOpen(true);
  };

  const handleEditClick = (user: User) => {
    setEditingUser(user);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (user: User) => {
    setUserToDelete(user);
    setIsDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (data: Partial<User>) => {
    if (editingUser) {
      await updateUser(editingUser.id, data);
      alert('User updated successfully.');
    } else {
      await createUser(data);
      alert('User created successfully.');
    }
    loadData();
  };

  const handleDeleteConfirm = async () => {
    if (userToDelete) {
      await deleteUser(userToDelete.id);
      alert('User deactivated successfully.');
      loadData();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Users</h1>
            <p className="text-gray-500 mt-1">Manage workers and application users</p>
          </div>
          <button
            onClick={handleAddClick}
            className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add User
          </button>
        </div>

        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6 flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search users..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
            />
          </div>
          
          <div className="flex gap-4 overflow-x-auto pb-2 md:pb-0">
            <div className="relative min-w-[150px]">
              <Filter className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <select
                value={factoryFilter}
                onChange={(e) => setFactoryFilter(e.target.value)}
                className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none appearance-none bg-white"
              >
                <option value="">All Factories</option>
                {factories.map(f => (
                  <option key={f.factory_id} value={f.factory_id}>{f.factory_name}</option>
                ))}
              </select>
            </div>
            
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="min-w-[130px] px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none bg-white"
            >
              <option value="all">All Roles</option>
              <option value="worker">Worker</option>
              <option value="supervisor">Supervisor</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
            </select>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="min-w-[130px] px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none bg-white"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>

        {error ? (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-red-800 mb-2">Error</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={loadData}
              className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors font-medium"
            >
              Retry
            </button>
          </div>
        ) : loading ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-500">Loading users...</p>
          </div>
        ) : (
          <UserTable 
            users={users} 
            onEdit={handleEditClick} 
            onDelete={handleDeleteClick} 
          />
        )}
      </main>

      <UserForm
        user={editingUser}
        factories={factories}
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleFormSubmit}
      />

      <DeleteUserDialog
        user={userToDelete}
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteConfirm}
      />
    </div>
  );
}
