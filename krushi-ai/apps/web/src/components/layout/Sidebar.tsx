'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Users, MessageSquare, LineChart, Leaf } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Farmers', href: '/farmers', icon: Users },
    { name: 'Conversations', href: '/conversations', icon: MessageSquare },
    { name: 'Crop Insights', href: '/insights', icon: LineChart },
  ];

  return (
    <div className="w-64 bg-green-900 text-white min-h-screen flex flex-col fixed inset-y-0 left-0 z-50">
      <div className="flex items-center justify-center h-20 border-b border-green-800">
        <Leaf className="w-8 h-8 text-green-400 mr-2" />
        <h1 className="text-2xl font-bold tracking-wider text-green-50">Krushi AI</h1>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-4 py-3 rounded-lg transition-colors duration-200 ${
                isActive
                  ? 'bg-green-800 text-green-50'
                  : 'text-green-100 hover:bg-green-800/50 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-green-800">
        <div className="flex items-center">
          <div className="w-8 h-8 rounded-full bg-green-700 flex items-center justify-center text-sm font-bold">
            AD
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium">Admin User</p>
            <p className="text-xs text-green-300">HQ Dashboard</p>
          </div>
        </div>
      </div>
    </div>
  );
}
