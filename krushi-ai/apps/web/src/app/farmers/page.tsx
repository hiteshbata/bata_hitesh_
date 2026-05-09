'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { Search } from 'lucide-react';

export default function FarmersPage() {
  const [farmers, setFarmers] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchFarmers() {
      const { data, error } = await supabase
        .from('farmers')
        .select(`
          id,
          phone_number,
          name,
          language_pref,
          created_at,
          villages(name)
        `)
        .order('created_at', { ascending: false })
        .limit(50);

      if (!error && data) {
        setFarmers(data);
      }
      setLoading(false);
    }
    fetchFarmers();
  }, []);

  const filteredFarmers = farmers.filter(f =>
    f.name?.toLowerCase().includes(search.toLowerCase()) ||
    f.villages?.name?.toLowerCase().includes(search.toLowerCase()) ||
    f.phone_number?.includes(search)
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">Farmers</h2>
          <p className="text-gray-500 mt-1">Manage registered farmers and their profiles</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100 bg-gray-50/50">
          <div className="relative max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search by name, phone, or village..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-600">
            <thead className="bg-gray-50 text-gray-700 uppercase font-semibold text-xs">
              <tr>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Phone / ID</th>
                <th className="px-6 py-4">Village</th>
                <th className="px-6 py-4">Language</th>
                <th className="px-6 py-4">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    Loading farmers...
                  </td>
                </tr>
              ) : filteredFarmers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No farmers found.
                  </td>
                </tr>
              ) : (
                filteredFarmers.map((farmer) => (
                  <tr key={farmer.id} className="hover:bg-green-50/30 transition-colors">
                    <td className="px-6 py-4 font-medium text-gray-900">{farmer.name || 'Unknown'}</td>
                    <td className="px-6 py-4">{farmer.phone_number}</td>
                    <td className="px-6 py-4">
                      {farmer.villages ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          {farmer.villages.name}
                        </span>
                      ) : (
                        <span className="text-gray-400 italic">Not set</span>
                      )}
                    </td>
                    <td className="px-6 py-4 uppercase">{farmer.language_pref}</td>
                    <td className="px-6 py-4">{new Date(farmer.created_at).toLocaleDateString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
