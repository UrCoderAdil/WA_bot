"use client";
import { useEffect, useState } from "react";
import Sidebar from "../../components/Sidebar";
import { fetchTenants, createTenant } from "../../lib/api";

export default function TenantsPage() {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    business_type: "restaurant",
    phone_number_id: "",
    system_prompt: "",
  });

  async function loadTenants() {
    try {
      const data = await fetchTenants();
      setTenants(data.tenants || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadTenants(); }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    await createTenant(form);
    setForm({ name: "", business_type: "restaurant", phone_number_id: "", system_prompt: "" });
    setShowForm(false);
    loadTenants();
  }

  const typeColors = {
    restaurant: "bg-amber-500/20 text-amber-300",
    clinic: "bg-emerald-500/20 text-emerald-300",
    fashion: "bg-pink-500/20 text-pink-300",
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Tenants</h1>
            <p className="text-gray-500 mt-1">Manage businesses on your platform</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-indigo-500 hover:bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition-colors"
          >
            + Add Tenant
          </button>
        </div>

        {/* Create Form */}
        {showForm && (
          <form onSubmit={handleSubmit} className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 mb-8 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input
                placeholder="Business Name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
                required
              />
              <select
                value={form.business_type}
                onChange={(e) => setForm({ ...form, business_type: e.target.value })}
                className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500 focus:outline-none"
              >
                <option value="restaurant">🍔 Restaurant</option>
                <option value="clinic">🏥 Clinic</option>
                <option value="fashion">👗 Fashion</option>
              </select>
              <input
                placeholder="WhatsApp Phone Number ID"
                value={form.phone_number_id}
                onChange={(e) => setForm({ ...form, phone_number_id: e.target.value })}
                className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
                required
              />
            </div>
            <textarea
              placeholder="Custom AI personality prompt (optional)"
              value={form.system_prompt}
              onChange={(e) => setForm({ ...form, system_prompt: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
              rows={3}
            />
            <button type="submit" className="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 rounded-xl text-sm font-medium transition-colors">
              Create Tenant
            </button>
          </form>
        )}

        {/* Tenants List */}
        {loading ? (
          <div className="flex items-center justify-center h-40">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : tenants.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tenants.map((t) => (
              <div key={t.id} className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 hover:border-indigo-500/30 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-white">{t.name}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${typeColors[t.business_type] || "bg-gray-700 text-gray-300"}`}>
                    {t.business_type}
                  </span>
                </div>
                <p className="text-xs text-gray-500 font-mono mb-2">ID: {t.phone_number_id}</p>
                {t.system_prompt && (
                  <p className="text-xs text-gray-400 line-clamp-2">{t.system_prompt}</p>
                )}
                <p className="text-xs text-gray-600 mt-3">Created: {new Date(t.created_at).toLocaleDateString()}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 text-gray-500">
            <p className="text-4xl mb-3">🏢</p>
            <p>No tenants registered yet. Add your first business!</p>
          </div>
        )}
      </main>
    </div>
  );
}
