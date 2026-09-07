/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Activity, Bell, UserCircle, LogOut, Menu, X } from 'lucide-react';
import { getSession, logout } from '@/../lib/auth';

interface User {
  username?: string;
  name?: string;
  email?: string;
  [key: string]: any;
}

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  
  const [user, setUser] = useState<User | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  
  // Future: fetch from notificationApi
  const [notifications] = useState<any[]>([]);

  const profileRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function loadUser() {
      const { data } = await getSession();
      if (data?.session) {
        setUser(data.session);
      }
    }
    loadUser();
  }, []);

  // Handle click outside to close dropdowns
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setIsNotificationOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
    setIsProfileOpen(false);
  };

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Factories', path: '/factories' },
    { name: 'Workers', path: '/workers' },
    { name: 'Users', path: '/users' },
    { name: 'Reports', path: '/reports' },
    { name: 'Devices', path: '/devices' },
  ];

  const displayName = user?.name || user?.username || user?.email || 'Authenticated User';
  const displaySecondary = user?.email || user?.username || '';

  return (
    <nav className="bg-gray-900 text-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Left Side: Logo & Desktop Navigation */}
          <div className="flex items-center">
            <Link href="/dashboard" className="flex items-center space-x-3 flex-shrink-0" aria-label="Smile Score Home">
              <Activity className="w-6 h-6 text-blue-500" />
              <span className="text-xl font-bold">Smile Score</span>
            </Link>
            
            <div className="hidden md:block ml-10">
              <div className="flex items-baseline space-x-4">
                {navLinks.map((link) => {
                  const isActive = pathname?.startsWith(link.path);
                  return (
                    <Link
                      key={link.name}
                      href={link.path}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive 
                          ? 'bg-gray-800 text-white' 
                          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                      }`}
                      aria-current={isActive ? 'page' : undefined}
                    >
                      {link.name}
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
          
          {/* Right Side: Notifications & Profile */}
          <div className="hidden md:flex items-center space-x-4">
            
            {/* Notifications */}
            <div className="relative" ref={notificationRef}>
              <button
                onClick={() => {
                  setIsNotificationOpen(!isNotificationOpen);
                  setIsProfileOpen(false);
                }}
                className="p-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded-full transition-colors relative"
                aria-label="Notifications"
              >
                <Bell className="w-5 h-5" />
                {notifications.length > 0 && (
                  <span className="absolute top-1 right-1 flex items-center justify-center w-4 h-4 text-[10px] font-bold text-white bg-red-500 rounded-full">
                    {notifications.length}
                  </span>
                )}
              </button>
              
              {isNotificationOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-white rounded-md shadow-lg py-1 border border-gray-200 text-gray-800 ring-1 ring-black ring-opacity-5">
                  <div className="px-4 py-2 border-b border-gray-100 font-semibold text-sm">
                    Notifications
                  </div>
                  <div className="max-h-60 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="px-4 py-6 text-sm text-center text-gray-500">
                        No new notifications
                      </div>
                    ) : (
                      notifications.map((n, i) => (
                        <div key={i} className="px-4 py-3 hover:bg-gray-50 border-b border-gray-50 text-sm">
                          {/* Future notification rendering */}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* User Profile */}
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => {
                  setIsProfileOpen(!isProfileOpen);
                  setIsNotificationOpen(false);
                }}
                className="flex items-center space-x-2 p-1 border-2 border-transparent text-gray-300 hover:text-white rounded-full transition-colors focus:outline-none focus:border-gray-700"
                aria-label="User profile"
              >
                <UserCircle className="w-7 h-7" />
              </button>
              
              {isProfileOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg py-1 border border-gray-200 text-gray-800 ring-1 ring-black ring-opacity-5">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <p className="text-sm font-semibold truncate text-gray-900">{displayName}</p>
                    {displaySecondary && displaySecondary !== displayName && (
                      <p className="text-xs truncate text-gray-500 mt-0.5">{displaySecondary}</p>
                    )}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
          
          {/* Mobile menu button */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {isMobileMenuOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-gray-700">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {navLinks.map((link) => {
              const isActive = pathname?.startsWith(link.path);
              return (
                <Link
                  key={link.name}
                  href={link.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`block px-3 py-2 rounded-md text-base font-medium ${
                    isActive 
                      ? 'bg-gray-800 text-white' 
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {link.name}
                </Link>
              );
            })}
          </div>
          <div className="pt-4 pb-3 border-t border-gray-700">
            <div className="flex items-center px-5">
              <div className="flex-shrink-0">
                <UserCircle className="h-10 w-10 text-gray-400" />
              </div>
              <div className="ml-3">
                <div className="text-base font-medium leading-none text-white">{displayName}</div>
                {displaySecondary && displaySecondary !== displayName && (
                  <div className="text-sm font-medium leading-none text-gray-400 mt-1">{displaySecondary}</div>
                )}
              </div>
              <button
                className="ml-auto flex-shrink-0 bg-gray-800 p-1 rounded-full text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white relative"
                onClick={() => {
                  setIsNotificationOpen(!isNotificationOpen);
                }}
              >
                <span className="sr-only">View notifications</span>
                <Bell className="h-6 w-6" />
                {notifications.length > 0 && (
                  <span className="absolute top-0 right-0 block h-2.5 w-2.5 rounded-full bg-red-500 ring-2 ring-gray-800" />
                )}
              </button>
            </div>
            
            {/* Mobile Notifications Preview */}
            {isNotificationOpen && (
              <div className="mt-3 px-2 space-y-1">
                {notifications.length === 0 ? (
                  <div className="px-3 py-2 text-sm text-gray-400">No new notifications</div>
                ) : (
                  <div className="px-3 py-2 text-sm text-gray-400">You have notifications</div>
                )}
              </div>
            )}
            
            <div className="mt-3 px-2 space-y-1">
              <button
                onClick={handleLogout}
                className="flex w-full items-center px-3 py-2 rounded-md text-base font-medium text-gray-400 hover:text-white hover:bg-gray-700"
              >
                <LogOut className="w-5 h-5 mr-3" />
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
