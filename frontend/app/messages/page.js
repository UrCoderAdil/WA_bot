"use client";
import { useEffect, useState } from "react";
import Sidebar from "../../components/Sidebar";
import { fetchMessages } from "../../lib/api";

export default function MessagesPage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchMessages(100);
        setMessages(data.messages || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Message Log</h1>
          <p className="text-gray-500 mt-1">Live feed of all conversations</p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-40">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : messages.length > 0 ? (
          <div className="space-y-3">
            {messages.map((msg) => (
              <div key={msg.id} className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 hover:border-gray-700 transition-colors">
                <div className="flex items-center gap-4 mb-2">
                  <span className="text-indigo-300 font-mono text-xs">{msg.phone_number}</span>
                  <span className="text-gray-600 text-xs">{new Date(msg.created_at).toLocaleString()}</span>
                  {msg.escalated && (
                    <span className="bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded text-xs">🚨 Escalated</span>
                  )}
                  {msg.tool_called && (
                    <span className="bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded text-xs">🛠️ {msg.tool_called}</span>
                  )}
                  {msg.response_time_ms && (
                    <span className="text-gray-500 text-xs">{Math.round(msg.response_time_ms)}ms</span>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-800/50 rounded-lg p-3">
                    <p className="text-xs text-gray-500 mb-1">👤 User</p>
                    <p className="text-sm text-gray-200">{msg.user_message || "-"}</p>
                  </div>
                  <div className="bg-indigo-900/20 rounded-lg p-3">
                    <p className="text-xs text-indigo-400 mb-1">🤖 AI</p>
                    <p className="text-sm text-gray-300">{msg.ai_response || "-"}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 text-gray-500">
            <p className="text-4xl mb-3">💬</p>
            <p>No messages yet. Messages will appear here as users chat with the bot.</p>
          </div>
        )}
      </main>
    </div>
  );
}
