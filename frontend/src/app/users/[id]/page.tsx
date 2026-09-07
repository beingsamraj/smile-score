/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { User, getUser } from '@/lib/userApi';
import { ArrowLeft, Loader2, User as UserIcon, Building2, Briefcase, Hash, Activity, Clock, CalendarDays } from 'lucide-react';
import Link from 'next/link';

export default function UserDetailsPage() {
  const { id } = useParams();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true);
        if (typeof id === 'string') {
          const data = await getUser(id);
          setUser(data);
        }
      } catch (err: any) {
        setError(err.message || 'User not found');
      } finally {
        setLoading(false);
      }
    };
    
    if (id) fetchUser();
  }, [id]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link href="/users" className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Users
          </Link>
        </div>

        {loading ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-500">Loading user details...</p>
          </div>
        ) : error || !user ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">User Not Found</h3>
            <p className="text-gray-500 mb-6">{error || 'The requested user could not be found.'}</p>
            <Link href="/users" className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
              Return to Users
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <UserIcon className="w-8 h-8 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{user.full_name}</h1>
                  <p className="text-gray-500 font-mono mt-1">{user.employee_code}</p>
                </div>
              </div>
              <div className="flex flex-col sm:items-end gap-2">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  user.status === 'active' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                }`}>
                  <Activity className="w-4 h-4 mr-1.5" />
                  {user.status === 'active' ? 'Active' : 'Inactive'}
                </span>
                <span className="text-sm text-gray-500 capitalize">{user.role}</span>
              </div>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4 border-b pb-2">User Details</h2>
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <Briefcase className="w-4 h-4 mr-2" /> Role
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 capitalize">{user.role}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <Building2 className="w-4 h-4 mr-2" /> Factory
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900">{user.factory_name || 'Not Assigned'}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <UserIcon className="w-4 h-4 mr-2" /> Contact
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {user.email && <div>{user.email}</div>}
                      {user.phone && <div>{user.phone}</div>}
                      {!user.email && !user.phone && <span className="text-gray-400">No contact info</span>}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <Hash className="w-4 h-4 mr-2" /> RFID UID
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 font-mono">
                      {user.rfid_uid || <span className="text-gray-400">Not Assigned</span>}
                    </dd>
                  </div>
                </dl>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4 border-b pb-2">System Info</h2>
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <CalendarDays className="w-4 h-4 mr-2" /> Created At
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {new Date(user.created_at).toLocaleString()}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <Clock className="w-4 h-4 mr-2" /> Last Updated
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {new Date(user.updated_at).toLocaleString()}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 flex items-center">
                      <Hash className="w-4 h-4 mr-2" /> System ID
                    </dt>
                    <dd className="mt-1 text-xs text-gray-500 font-mono break-all">
                      {user.id}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>

            {/* Placeholder for future sections */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4 border-b pb-2">Activity & Analytics</h2>
              <div className="py-8 text-center bg-gray-50 rounded-lg border border-dashed border-gray-200">
                <p className="text-gray-500 text-sm">No data available</p>
                <p className="text-xs text-gray-400 mt-1">Smile Score and Activity records will appear here.</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
