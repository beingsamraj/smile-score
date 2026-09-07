/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { Device, getDevice } from '@/lib/deviceApi';
import { ArrowLeft, Loader2, Server, Building2, MapPin, Hash, Activity, Clock, CalendarDays, Radio, Cpu, Network } from 'lucide-react';
import Link from 'next/link';

export default function DeviceDetailsPage() {
  const { id } = useParams();
  const [device, setDevice] = useState<Device | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDevice = async () => {
      try {
        setLoading(true);
        if (typeof id === 'string') {
          const data = await getDevice(id);
          setDevice(data);
        }
      } catch (err: any) {
        setError(err.message || 'Device not found');
      } finally {
        setLoading(false);
      }
    };
    
    if (id) fetchDevice();
  }, [id]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-50 text-green-700';
      case 'offline': return 'bg-red-50 text-red-700';
      case 'maintenance': return 'bg-amber-50 text-amber-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <Link href="/devices" className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Devices
          </Link>
        </div>

        {loading ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-500">Loading device details...</p>
          </div>
        ) : error || !device ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Device Not Found</h3>
            <p className="text-gray-500 mb-6">{error || 'The requested device could not be found.'}</p>
            <Link href="/devices" className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
              Return to Devices
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Server className="w-8 h-8 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{device.device_name}</h1>
                  <p className="text-gray-500 font-mono mt-1">{device.device_code}</p>
                </div>
              </div>
              <div className="flex flex-col sm:items-end gap-2">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(device.status)}`}>
                  <Activity className="w-4 h-4 mr-1.5" />
                  {device.status.charAt(0).toUpperCase() + device.status.slice(1)}
                </span>
                <span className="text-sm text-gray-500 capitalize flex items-center">
                  <Cpu className="w-3.5 h-3.5 mr-1" />
                  {device.device_type.replace('_', ' ')}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Details */}
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <h2 className="text-lg font-bold text-gray-900 mb-4 border-b pb-2">Device Information</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <dl className="space-y-4">
                      <div>
                        <dt className="text-sm font-medium text-gray-500 flex items-center">
                          <Building2 className="w-4 h-4 mr-2" /> Factory
                        </dt>
                        <dd className="mt-1 text-sm text-gray-900">{device.factory_name || 'Not Assigned'}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500 flex items-center">
                          <MapPin className="w-4 h-4 mr-2" /> Location
                        </dt>
                        <dd className="mt-1 text-sm text-gray-900">{device.location || 'Not Assigned'}</dd>
                      </div>
                    </dl>
                    <dl className="space-y-4">
                      <div>
                        <dt className="text-sm font-medium text-gray-500 flex items-center">
                          <Network className="w-4 h-4 mr-2" /> MAC Address
                        </dt>
                        <dd className="mt-1 text-sm text-gray-900 font-mono">
                          {device.mac_address || <span className="text-gray-400">Unknown</span>}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500 flex items-center">
                          <Hash className="w-4 h-4 mr-2" /> Firmware Version
                        </dt>
                        <dd className="mt-1 text-sm text-gray-900 font-mono">
                          {device.firmware_version || <span className="text-gray-400">Unknown</span>}
                        </dd>
                      </div>
                    </dl>
                  </div>
                  
                  {device.description && (
                    <div className="mt-6 pt-4 border-t border-gray-50">
                      <h3 className="text-sm font-medium text-gray-500 mb-2">Description</h3>
                      <p className="text-sm text-gray-800 bg-gray-50 p-3 rounded-lg border border-gray-100">
                        {device.description}
                      </p>
                    </div>
                  )}
                </div>

                {/* Future Telemetry Section */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <h2 className="text-lg font-bold text-gray-900 mb-4 border-b pb-2 flex items-center justify-between">
                    <span>Recent Activity</span>
                    <span className="text-xs font-normal text-blue-600 bg-blue-50 px-2 py-1 rounded-md">Coming Soon</span>
                  </h2>
                  <div className="py-12 text-center bg-gray-50 rounded-lg border border-dashed border-gray-200">
                    <Radio className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    <p className="text-gray-500 text-sm font-medium">No telemetry data available</p>
                    <p className="text-xs text-gray-400 mt-1 max-w-sm mx-auto">
                      Future integration will display RFID scans, Button presses, and Emotion events reported by this device.
                    </p>
                  </div>
                </div>
              </div>

              {/* Right Column - Status & System */}
              <div className="space-y-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <h2 className="text-lg font-bold text-gray-900 mb-4 border-b pb-2">Device Status</h2>
                  
                  <div className="mb-6 text-center py-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Last Heartbeat</p>
                    <p className="text-lg font-medium text-gray-900">
                      {device.last_seen ? new Date(device.last_seen).toLocaleString() : 'Never'}
                    </p>
                    {device.last_seen && (
                      <p className="text-xs text-gray-400 mt-1">
                        Active {device.status === 'online' ? 'currently' : 'previously'}
                      </p>
                    )}
                  </div>

                  <dl className="space-y-4">
                    <div>
                      <dt className="text-sm font-medium text-gray-500 flex items-center">
                        <CalendarDays className="w-4 h-4 mr-2" /> Registered On
                      </dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(device.created_at).toLocaleDateString()}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500 flex items-center">
                        <Clock className="w-4 h-4 mr-2" /> Last Modified
                      </dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        {new Date(device.updated_at).toLocaleString()}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
