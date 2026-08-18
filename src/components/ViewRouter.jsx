import { useState } from 'react'

export default function ViewRouter({ views, defaultView, children }) {
  const [active, setActive] = useState(defaultView || views[0]?.id)

  return (
    <div>
      {/* Tab bar */}
      <div className="mb-5 flex items-center gap-1 rounded-lg bg-white/[0.03] border border-white/10 p-1">
        {views.map((view) => (
          <button
            key={view.id}
            onClick={() => setActive(view.id)}
            className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-all ${
              active === view.id
                ? 'bg-white/10 text-white shadow-sm'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            {view.label}
          </button>
        ))}
      </div>

      {/* Active view content */}
      {children?.[active]}
    </div>
  )
}
