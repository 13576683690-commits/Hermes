import { useState, useEffect } from 'react'
import ArchiveCard from './components/ArchiveCard.jsx'
import StatsGrid from './components/StatsGrid.jsx'
import ViewRouter from './components/ViewRouter.jsx'

const views = [
  { id: 'archives', label: 'Archives' },
  { id: 'memory', label: 'Memory' },
  { id: 'evolution', label: 'Evolution' },
]

function TimelineList({ title, items }) {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-sm font-medium uppercase text-teal-300/80">{title}</p>
        <h2 className="mt-2 text-2xl font-semibold text-white sm:text-3xl">Knowledge stream</h2>
      </div>
      <div className="grid gap-3">
        {items.map((item, index) => (
          <article
            key={index}
            className="rounded-lg border border-white/10 bg-white/[0.04] p-5 shadow-lg shadow-black/10"
          >
            <p className="text-sm leading-6 text-slate-200">{item.content}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

export default function App() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('./data.json')
      .then((res) => res.json())
      .then(setData)
      .catch(() => {
        // Fallback for dev server
        fetch('/data.json').then((res) => res.json()).then(setData)
      })
  }, [])

  if (!data)
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-400">
        <div className="text-center">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-indigo-400" />
          <p className="text-sm">Loading Archive...</p>
        </div>
      </div>
    )

  const archives = data.archives ?? []
  const sorted = [...archives].sort((a, b) => (a.date < b.date ? 1 : -1))

  return (
    <main className="min-h-screen text-slate-100">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="flex flex-col items-center justify-center py-12 text-center">
          <div className="mb-4 flex h-20 w-20 items-center justify-center overflow-hidden rounded-full border border-white/5 bg-slate-800/50 shadow-2xl">
            <img src="./avatar.png" alt="Avatar" className="h-full w-full object-cover" />
          </div>
          <h1 className="text-5xl font-bold tracking-tight text-white">进化档案馆</h1>
          <p className="mt-4 text-slate-400">Hermes 和 锅仔 的共同进化史</p>
          <div className="mt-8 flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-emerald-500"></span>
            <span className="text-xs text-emerald-400">
              SYSTEM ACTIVE: {new Date().toISOString().replace('T', ' ').substring(0, 16)}
            </span>
          </div>
        </header>

        {/* Stats */}
        <StatsGrid stats={data.stats} />

        {/* Views */}
        <ViewRouter views={views} defaultView="archives">
          {{
            archives: (
              <section className="grid gap-5 lg:grid-cols-2">
                {sorted.map((archive) => (
                  <ArchiveCard key={archive.id} archive={archive} />
                ))}
              </section>
            ),
            memory: <TimelineList title="Memory" items={data.memories ?? []} />,
            evolution: <TimelineList title="Evolution" items={data.evolutions ?? []} />,
          }}
        </ViewRouter>

        {/* Footer */}
        <footer className="mt-8 border-t border-white/5 py-6 text-center">
          <p className="text-xs text-slate-600">
            AI Evolution Dashboard · Powered by Hermes & React/Vite/Tailwind · GitHub Pages
          </p>
        </footer>
      </div>
    </main>
  )
}
