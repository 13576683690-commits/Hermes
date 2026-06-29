const labels = {
  archives: "Archives",
  points: "Points",
  skills: "Skills",
};

export default function StatsGrid({ stats = {} }) {
  const entries = Object.entries(stats);

  return (
    <section
      className="grid w-full grid-cols-3 gap-3 lg:max-w-md"
      aria-label="Dashboard summary"
    >
      {entries.map(([key, value]) => (
        <div
          key={key}
          className="rounded-lg border border-white/10 bg-white/[0.05] p-4 text-center shadow-lg shadow-black/10"
        >
          <p className="text-2xl font-bold text-white sm:text-3xl">{value}</p>
          <p className="mt-1 text-xs font-medium uppercase text-slate-400">
            {labels[key] ?? key}
          </p>
        </div>
      ))}
    </section>
  );
}
