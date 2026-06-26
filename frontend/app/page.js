"use client";
import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import StatCard from "../components/StatCard";
import { fetchSummary, fetchMessages } from "../lib/api";

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const [summaryData, messagesData] = await Promise.all([
          fetchSummary(24),
          fetchMessages(20),
        ]);
        setSummary(summaryData);
        setMessages(messagesData.messages || []);
      } catch (err) {
        setError("Cannot connect to API. Make sure the FastAPI server is running on port 8000.");
      } finally {
        setLoading(false);
      }
    }
    load();
    // Auto-refresh every 30 seconds
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Analytics Dashboard</h1>
          <p className="text-gray-500 mt-1">Real-time overview of your WhatsApp AI platform</p>
        </div>

        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 mb-6 text-rose-300 text-sm">
            ⚠️ {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Messages"
                value={summary?.total_messages || 0}
                subtitle="Last 24 hours"
                icon="💬"
                color="indigo"
              />
              <StatCard
                title="Active Users"
                value={summary?.active_users || 0}
                subtitle="Unique phone numbers"
                icon="👥"
                color="cyan"
              />
              <StatCard
                title="Avg Response Time"
                value={`${summary?.avg_response_time_ms || 0}ms`}
                subtitle="Target: < 3000ms"
                icon="⚡"
                color="emerald"
              />
              <StatCard
                title="Escalation Rate"
                value={`${summary?.escalation_rate || 0}%`}
                subtitle={`${summary?.escalations || 0} escalations`}
                icon="🚨"
                color="rose"
              />
            </div>

            {/* Tool Usage & Message Types Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Tool Usage */}
              <div className="bg-gray-900/60 backdrop-blur-sm border border-gray-800 rounded-2xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">🛠️ Tool Usage</h2>
                {summary?.tool_usage && Object.keys(summary.tool_usage).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(summary.tool_usage).map(([tool, count]) => (
                      <div key={tool} className="flex items-center justify-between">
                        <span className="text-sm text-gray-300 font-mono">{tool}</span>
                        <span className="bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-full text-xs font-bold">
                          {count}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No tool usage data yet</p>
                )}
              </div>

              {/* Message Types */}
              <div className="bg-gray-900/60 backdrop-blur-sm border border-gray-800 rounded-2xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">📨 Message Types</h2>
                {summary?.message_types && Object.keys(summary.message_types).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(summary.message_types).map(([type, count]) => {
                      const icons = { text: "💬", image: "🖼️", voice: "🎤" };
                      return (
                        <div key={type} className="flex items-center justify-between">
                          <span className="text-sm text-gray-300">
                            {icons[type] || "📄"} {type.charAt(0).toUpperCase() + type.slice(1)}
                          </span>
                          <span className="bg-cyan-500/20 text-cyan-300 px-3 py-1 rounded-full text-xs font-bold">
                            {count}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No message data yet</p>
                )}
              </div>
            </div>

            {/* Recent Messages */}
            <div className="bg-gray-900/60 backdrop-blur-sm border border-gray-800 rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">💬 Recent Messages</h2>
              {messages.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-800 text-gray-400">
                        <th className="text-left py-3 px-2">Phone</th>
                        <th className="text-left py-3 px-2">Message</th>
                        <th className="text-left py-3 px-2">Response</th>
                        <th className="text-left py-3 px-2">Tool</th>
                        <th className="text-left py-3 px-2">Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {messages.map((msg) => (
                        <tr key={msg.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                          <td className="py-3 px-2 text-indigo-300 font-mono text-xs">
                            {msg.phone_number}
                          </td>
                          <td className="py-3 px-2 text-gray-300 max-w-xs truncate">
                            {msg.user_message || "-"}
                          </td>
                          <td className="py-3 px-2 text-gray-400 max-w-xs truncate">
                            {msg.ai_response?.substring(0, 80) || "-"}
                          </td>
                          <td className="py-3 px-2">
                            {msg.tool_called ? (
                              <span className="bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded text-xs">
                                {msg.tool_called}
                              </span>
                            ) : (
                              <span className="text-gray-600">-</span>
                            )}
                          </td>
                          <td className="py-3 px-2 text-gray-500 text-xs">
                            {msg.response_time_ms ? `${Math.round(msg.response_time_ms)}ms` : "-"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No messages yet. Start chatting with your bot!</p>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
