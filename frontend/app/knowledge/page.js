"use client";
import { useEffect, useState } from "react";
import Sidebar from "../../components/Sidebar";
import { fetchKnowledge, addKnowledge, deleteKnowledge } from "../../lib/api";

export default function KnowledgePage() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", content: "", category: "faq" });

  async function loadEntries() {
    try {
      const data = await fetchKnowledge();
      setEntries(data.entries || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadEntries(); }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    await addKnowledge(form);
    setForm({ title: "", content: "", category: "faq" });
    setShowForm(false);
    loadEntries();
  }

  async function handleDelete(id) {
    await deleteKnowledge(id);
    loadEntries();
  }

  const categoryColors = {
    faq: "bg-indigo-500/20 text-indigo-300",
    menu: "bg-amber-500/20 text-amber-300",
    policy: "bg-cyan-500/20 text-cyan-300",
    product: "bg-pink-500/20 text-pink-300",
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Knowledge Base</h1>
            <p className="text-gray-500 mt-1">Train the AI with your business-specific information</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-indigo-500 hover:bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition-colors"
          >
            + Add Entry
          </button>
        </div>

        {/* Create Form */}
        {showForm && (
          <form onSubmit={handleSubmit} className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 mb-8 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                placeholder="Title (e.g., Return Policy)"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
                required
              />
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500 focus:outline-none"
              >
                <option value="faq">❓ FAQ</option>
                <option value="menu">🍽️ Menu</option>
                <option value="policy">📋 Policy</option>
                <option value="product">🛍️ Product</option>
              </select>
            </div>
            <textarea
              placeholder="Content (e.g., Our return policy allows returns within 7 days of purchase...)"
              value={form.content}
              onChange={(e) => setForm({ ...form, content: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
              rows={4}
              required
            />
            <button type="submit" className="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 rounded-xl text-sm font-medium transition-colors">
              Save Entry
            </button>
          </form>
        )}

        {/* Entries */}
        {loading ? (
          <div className="flex items-center justify-center h-40">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : entries.length > 0 ? (
          <div className="space-y-4">
            {entries.map((entry) => (
              <div key={entry.id} className="bg-gray-900/60 border border-gray-800 rounded-2xl p-5 hover:border-indigo-500/30 transition-colors group">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-base font-semibold text-white">{entry.title}</h3>
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${categoryColors[entry.category] || "bg-gray-700 text-gray-300"}`}>
                        {entry.category}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 leading-relaxed">{entry.content}</p>
                  </div>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="text-gray-600 hover:text-rose-400 transition-colors opacity-0 group-hover:opacity-100 ml-4 text-lg"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 text-gray-500">
            <p className="text-4xl mb-3">📚</p>
            <p>No knowledge entries yet. Add your FAQs, menu items, or policies!</p>
          </div>
        )}
      </main>
    </div>
  );
}
