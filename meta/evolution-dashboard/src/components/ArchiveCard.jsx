import { useMemo, useState } from "react";

const detailLabels = {
  skill: "Skill",
  evolution: "Evolution",
  memory: "Memory",
  node: "Node",
};

export default function ArchiveCard({ archive }) {
  const [copied, setCopied] = useState(false);

  const details = useMemo(() => {
    return Object.entries(archive.details ?? {}).flatMap(([group, items]) =>
      items.map((item) => ({ ...item, group }))
    );
  }, [archive.details]);

  async function copyCommand() {
    if (!archive.command) return;

    try {
      await navigator.clipboard.writeText(archive.command);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  }

  return (
    <article className="flex h-full flex-col rounded-lg border border-white/10 bg-slate-950/70 p-5 shadow-2xl shadow-black/20 backdrop-blur">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-medium text-teal-300">{archive.date}</p>
          <h2 className="mt-2 text-2xl font-semibold leading-tight text-white">
            {archive.title}
          </h2>
        </div>
        {archive.command && (
          <button
            type="button"
            onClick={copyCommand}
            className="inline-flex h-10 shrink-0 items-center justify-center rounded-md border border-teal-300/40 px-3 text-sm font-medium text-teal-100 transition hover:border-teal-200 hover:bg-teal-300/10 focus:outline-none focus:ring-2 focus:ring-teal-300/60"
            aria-label="Copy archive command"
          >
            {copied ? "Copied" : "Copy"}
          </button>
        )}
      </div>

      <p className="mt-4 text-sm leading-6 text-slate-300">{archive.desc}</p>

      <div className="mt-5 flex flex-wrap gap-2">
        {(archive.tags ?? []).map((tag) => (
          <span
            key={tag}
            className="rounded-full border border-white/10 bg-white/[0.06] px-3 py-1 text-xs font-medium text-slate-200"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        {details.map((item) => (
          <div
            key={`${item.group}-${item.title}`}
            className="rounded-lg border border-white/10 bg-white/[0.04] p-4"
          >
            <div className="flex items-center gap-3">
              <span className="text-xl" aria-hidden="true">
                {item.icon}
              </span>
              <div>
                <p className="text-xs font-semibold uppercase text-teal-200/80">
                  {detailLabels[item.group] ?? item.group}
                </p>
                <h3 className="text-sm font-semibold text-white">
                  {item.title}
                </h3>
              </div>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              {item.content}
            </p>
          </div>
        ))}
      </div>

      {archive.command && (
        <code className="mt-5 block overflow-x-auto rounded-md border border-white/10 bg-black/30 px-3 py-2 text-xs text-slate-300">
          {archive.command}
        </code>
      )}
    </article>
  );
}
