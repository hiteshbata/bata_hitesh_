'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { MessageCircle, Bot, User, Filter } from 'lucide-react';

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'AI' | 'USER'>('ALL');

  useEffect(() => {
    async function fetchConversations() {
      const { data, error } = await supabase
        .from('conversations')
        .select(`
          id,
          message_body,
          sender,
          timestamp,
          farmers(name, phone_number)
        `)
        .order('timestamp', { ascending: false })
        .limit(100);

      if (!error && data) {
        setConversations(data);
      }
      setLoading(false);
    }
    fetchConversations();
  }, []);

  const filteredConversations = conversations.filter(c => {
    if (filter === 'ALL') return true;
    return filter.toLowerCase() === c.sender;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">Live Conversations</h2>
          <p className="text-gray-500 mt-1">Real-time message logs between farmers and Krushi AI</p>
        </div>

        <div className="flex items-center space-x-2 bg-white rounded-lg border border-gray-200 p-1 shadow-sm">
          <Filter className="w-4 h-4 text-gray-400 ml-2" />
          <select
            className="border-none text-sm focus:ring-0 text-gray-600 cursor-pointer"
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
          >
            <option value="ALL">All Messages</option>
            <option value="USER">Farmers Only</option>
            <option value="AI">AI Responses Only</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="divide-y divide-gray-100 max-h-[75vh] overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading messages...</div>
          ) : filteredConversations.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No messages found.</div>
          ) : (
            filteredConversations.map((msg) => (
              <div key={msg.id} className={`p-6 flex gap-4 hover:bg-gray-50 transition-colors ${msg.sender === 'ai' ? 'bg-green-50/20' : ''}`}>
                <div className="flex-shrink-0 mt-1">
                  {msg.sender === 'ai' ? (
                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-green-600" />
                    </div>
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <User className="w-5 h-5 text-blue-600" />
                    </div>
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-gray-900">
                      {msg.sender === 'ai' ? 'Krushi AI' : (msg.farmers?.name || 'Unknown Farmer')}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(msg.timestamp).toLocaleString()}
                    </span>
                  </div>

                  {msg.sender === 'user' && msg.farmers?.phone_number && (
                    <div className="text-xs text-gray-400 mb-2 font-mono">
                      {msg.farmers.phone_number.includes('telegram')
                        ? 'Via Telegram Bot'
                        : 'Via WhatsApp'}
                    </div>
                  )}

                  <p className="text-gray-700 whitespace-pre-wrap leading-relaxed text-sm">
                    {msg.message_body}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
