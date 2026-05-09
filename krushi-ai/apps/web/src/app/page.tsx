'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { Users, MessageCircle, Bot, AlertTriangle } from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    farmers: 0,
    conversations: 0,
    alerts: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      // For MVP, we fetch counts directly. In production, use a secure API endpoint.
      try {
        const [farmersRes, convosRes] = await Promise.all([
          supabase.from('farmers').select('*', { count: 'exact', head: true }),
          supabase.from('conversations').select('*', { count: 'exact', head: true })
        ]);

        setStats({
          farmers: farmersRes.count || 0,
          conversations: convosRes.count || 0,
          alerts: 0 // Mock alerts for MVP
        });
      } catch (err) {
        console.error("Error fetching stats:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">Overview</h2>
          <p className="text-gray-500 mt-1">Daily metrics for Krushi AI Assistant</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Farmers"
          value={loading ? "..." : stats.farmers}
          icon={<Users className="w-6 h-6 text-blue-600" />}
          bgColor="bg-blue-50"
        />
        <StatCard
          title="Conversations"
          value={loading ? "..." : stats.conversations}
          icon={<MessageCircle className="w-6 h-6 text-green-600" />}
          bgColor="bg-green-50"
        />
        <StatCard
          title="Active Bots"
          value="2 (WA, TG)"
          icon={<Bot className="w-6 h-6 text-purple-600" />}
          bgColor="bg-purple-50"
        />
        <StatCard
          title="Recent Alerts"
          value={loading ? "..." : stats.alerts}
          icon={<AlertTriangle className="w-6 h-6 text-red-600" />}
          bgColor="bg-red-50"
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mt-8">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">System Status</h3>
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <span className="w-3 h-3 rounded-full bg-green-500 mr-2 animate-pulse"></span>
            <span className="text-sm font-medium text-gray-600">FastAPI Backend (Online)</span>
          </div>
          <div className="flex items-center">
            <span className="w-3 h-3 rounded-full bg-green-500 mr-2 animate-pulse"></span>
            <span className="text-sm font-medium text-gray-600">Celery Queue (Online)</span>
          </div>
          <div className="flex items-center">
            <span className="w-3 h-3 rounded-full bg-green-500 mr-2 animate-pulse"></span>
            <span className="text-sm font-medium text-gray-600">Supabase DB (Online)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, bgColor }: { title: string, value: string | number, icon: React.ReactNode, bgColor: string }) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center space-x-4">
      <div className={`p-4 rounded-lg ${bgColor}`}>
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <h4 className="text-2xl font-bold text-gray-900">{value}</h4>
      </div>
    </div>
  );
}
