const statItems = [
  { key: 'archives', label: '归档', icon: '📦' },
  { key: 'points', label: '进化点', icon: '⚡' },
  { key: 'skills', label: 'Skill', icon: '🔧' },
]

export default function StatsGrid({ stats }) {
  return (
    <section className="grid grid-cols-3 gap-3 sm:gap-4">
      {statItems.map(({ key, label, icon }) => (
        <div
          key={key}
          className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-center sm:py-4"
        >
          <div className="text-2xl font-bold text-white sm:text-3xl">
            {stats?.[key] ?? 0}
          </div>
          <div className="mt-0.5 text-xs text-slate-500 sm:text-sm">
            {icon} {label}
          </div>
        </div>
      ))}
    </section>
  )
}
