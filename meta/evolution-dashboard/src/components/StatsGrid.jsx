const labels = {
  archives: "Archives",
  points: "Points",
  skills: "Skills",
};

export default function StatsGrid({ stats = {} }) {
  const labels = {
    archives: "档案总数",
    points: "累计进化点",
    skills: "共建 Skills",
  };

  const dailyLabels = {
    archives: "今日新增档案",
    points: "今日进化点",
    skills: "今日共建 Skills",
  };

  // 假设 stats 包含 { archives, points, skills } 以及对应的 daily_xxx
  return (
    <div className="flex flex-col gap-4">
      {/* 顶部主统计区 */}
      <section className="grid w-full grid-cols-3 gap-6" aria-label="Main stats">
        {Object.entries(labels).map(([key, label]) => (
          <div
            key={key}
            className="rounded-2xl border border-white/5 bg-slate-800/50 p-8 text-center shadow-xl"
          >
            <p className="text-5xl font-bold text-white">{stats[key] || 0}</p>
            <p className="mt-2 text-sm font-medium text-slate-400">{label}</p>
          </div>
        ))}
      </section>

      {/* 底部今日增量区 */}
      <section className="grid w-full grid-cols-3 gap-6" aria-label="Daily stats">
        {Object.entries(dailyLabels).map(([key, label]) => (
          <div
            key={`daily-${key}`}
            className="rounded-2xl border border-white/5 bg-slate-800/30 p-6 text-center"
          >
            <p className="text-3xl font-semibold text-emerald-400">+{stats[`daily_${key}`] || 0}</p>
            <p className="mt-1 text-xs text-slate-500 uppercase">{label}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
