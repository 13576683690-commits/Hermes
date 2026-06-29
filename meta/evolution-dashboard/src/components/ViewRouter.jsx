import { useState } from "react";

export default function ViewRouter({ views, defaultView, children }) {
  const [activeView, setActiveView] = useState(defaultView ?? views[0]?.id);

  return (
    <div className="space-y-6">
      <nav
        className="flex w-full gap-2 overflow-x-auto rounded-lg border border-white/10 bg-black/20 p-1"
        aria-label="Dashboard views"
      >
        {views.map((view) => {
          const isActive = view.id === activeView;

          return (
            <button
              key={view.id}
              type="button"
              onClick={() => setActiveView(view.id)}
              className={[
                "h-11 min-w-32 rounded-md px-4 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-teal-300/60",
                isActive
                  ? "bg-teal-300 text-slate-950 shadow-lg shadow-teal-950/30"
                  : "text-slate-300 hover:bg-white/10 hover:text-white",
              ].join(" ")}
              aria-pressed={isActive}
            >
              {view.label}
            </button>
          );
        })}
      </nav>

      <div>{children[activeView]}</div>
    </div>
  );
}
