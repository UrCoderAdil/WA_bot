"use client";
import { useEffect, useState } from "react";
import Sidebar from "../../components/Sidebar";
import { fetchCustomers } from "../../lib/api";

export default function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchCustomers();
        setCustomers(data.customers || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Customers</h1>
          <p className="text-gray-500 mt-1">CRM — All customer profiles tracked by the AI</p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-40">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : customers.length > 0 ? (
          <div className="bg-gray-900/60 border border-gray-800 rounded-2xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 bg-gray-900/40">
                  <th className="text-left py-4 px-4">Phone</th>
                  <th className="text-left py-4 px-4">Name</th>
                  <th className="text-left py-4 px-4">Language</th>
                  <th className="text-left py-4 px-4">Orders</th>
                  <th className="text-left py-4 px-4">Tags</th>
                  <th className="text-left py-4 px-4">Last Active</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c) => (
                  <tr key={c.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                    <td className="py-3 px-4 text-indigo-300 font-mono">{c.phone_number}</td>
                    <td className="py-3 px-4 text-white">{c.name || "-"}</td>
                    <td className="py-3 px-4 text-gray-400">{c.preferred_language}</td>
                    <td className="py-3 px-4 text-cyan-300">{c.total_orders}</td>
                    <td className="py-3 px-4">
                      {(c.tags || []).map((tag) => (
                        <span key={tag} className="bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded text-xs mr-1">
                          {tag}
                        </span>
                      ))}
                    </td>
                    <td className="py-3 px-4 text-gray-500 text-xs">
                      {new Date(c.last_interaction).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-16 text-gray-500">
            <p className="text-4xl mb-3">👥</p>
            <p>No customers yet. Customer profiles are created automatically when users chat with the bot.</p>
          </div>
        )}
      </main>
    </div>
  );
}
