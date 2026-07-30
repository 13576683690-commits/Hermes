import { useState } from 'react'

const categoryLabels = {
  skill: { label: 'Skill', color: 'text-indigo-300', bg: 'bg-indigo-500/10', border: 'border-indigo-500/20' },
  memory: { label: '记忆点', color: 'text-emerald-300', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  evolution: { label: '进化点', color: 'text-amber-300', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  node: { label: '探索节点', color: 'text-rose-300', bg: 'bg-rose-500/10', border: 'border-rose-500/20' },
}

export default function ArchiveCard({ archive }) {
  const [expanded, setExpanded] = useState(false)
  const [copied, setCopied] = useState(false)

  const copyCommand = (e) => {
    e.stopPropagation()
    const cmd = archive.command || ''
    navigator.clipboard?.writeText(cmd).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  const totalStats = Object.values(archive.stats || {}).reduce((a, b) => a + b, 0)

  return (
    <article
      className="archive-card rounded-xl border border-white/10 bg-white/[0.03] p-6 shadow-lg shadow-black/20 transition-all duration-300 hover:border-white/20 hover:bg-white/[0.05]"
      onClick={() => setExpanded(!expanded)}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <time>{archive.date}</time>
            <span>·</span>
            <span>{totalStats} 项提炼</span>
          </div>
          <h3 className="mt-1.5 text-lg font-semibold text-white">{archive.title}</h3>
        </div>
        <svg
          className={`mt-1 h-4 w-4 shrink-0 text-slate-500 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {/* Description */}
      <p className="mt-2 text-sm leading-6 text-slate-400">{archive.desc}</p>

      {/* Tags */}
      {archive.tags?.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {archive.tags.map((tag, i) => (
            <span key={i} className="rounded-md bg-white/5 px-2 py-0.5 text-xs text-slate-400">
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Expanded details */}
      {expanded && archive.details && (
        <div className="mt-4 space-y-3 border-t border-white/10 pt-4">
          {Object.entries(categoryLabels).map(([key, cfg]) => {
            const items = archive.details[key]
            if (!items?.length) return null
            return (
              <div key={key} className="space-y-1.5">
                <p className={`text-xs font-medium uppercase ${cfg.color}`}>{cfg.label}</p>
                {items.map((item, i) => (
                  <div key={i} className={`rounded-lg ${cfg.bg} ${cfg.border} border p-3`}>
                    <p className="text-sm font-medium text-slate-200">
                      {item.icon} {item.title}
                    </p>
                    <p className="mt-0.5 text-xs leading-5 text-slate-400">{item.content}</p>
                  </div>
                ))}
              </div>
            )
          })}

          {/* Command */}
          {archive.command && (
            <div
              className="copy-command mt-2 flex items-center gap-2 rounded-lg bg-slate-800/50 border border-white/5 px-3 py-2"
              onClick={copyCommand}
            >
              <code className="flex-1 text-xs text-emerald-400 font-mono">$ {archive.command}</code>
              <span className="text-xs text-slate-500">{copied ? '✓ 已复制' : '点击复制'}</span>
            </div>
          )}
        </div>
      )}
    </article>
  )
}
