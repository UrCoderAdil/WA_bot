export default function StatCard({ title, value, subtitle, icon, color = "indigo" }) {
  const colorMap = {
    indigo: "from-indigo-500/20 to-indigo-600/10 border-indigo-500/30 text-indigo-300",
    cyan: "from-cyan-500/20 to-cyan-600/10 border-cyan-500/30 text-cyan-300",
    emerald: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/30 text-emerald-300",
    amber: "from-amber-500/20 to-amber-600/10 border-amber-500/30 text-amber-300",
    rose: "from-rose-500/20 to-rose-600/10 border-rose-500/30 text-rose-300",
  };

  return (
    <div
      className={`bg-gradient-to-br ${colorMap[color]} border rounded-2xl p-6 backdrop-blur-sm transition-transform hover:scale-[1.02] duration-200`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-gray-400">{title}</span>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
      {subtitle && (
        <p className="text-xs text-gray-400 mt-2">{subtitle}</p>
      )}
    </div>
  );
}
