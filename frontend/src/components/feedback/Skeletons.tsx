/**
 * Loading skeletons that mirror the shape of each view, so the layout stays
 * stable while data loads. All use the shared `.skeleton` shimmer.
 */

function Bar({ width = '100%', height = 14 }: { width?: string | number; height?: number }) {
  return <div className="skeleton" style={{ width, height, borderRadius: 6 }} />;
}

/**
 * Skeleton rows for list/table pages (applications list, offers, interviews).
 * Renders only the card body so callers that already provide a `.card` wrapper
 * don't nest cards.
 */
export function TableSkeleton({ rows = 6, columns = 5 }: { rows?: number; columns?: number }) {
  return (
    <div className="card-body stack" aria-busy="true" aria-label="Loading">
      {Array.from({ length: rows }).map((_, r) => (
        <div
          key={r}
          className="row"
          style={{ justifyContent: 'space-between', gap: 'var(--space-4)' }}
        >
          {Array.from({ length: columns }).map((__, c) => (
            <Bar key={c} width={c === 0 ? '24%' : `${Math.floor(60 / (columns - 1))}%`} />
          ))}
        </div>
      ))}
    </div>
  );
}

/** Skeleton for the applications Kanban board. */
export function BoardSkeleton({ columns = 5 }: { columns?: number }) {
  return (
    <div className="kanban" aria-busy="true" aria-label="Loading board">
      {Array.from({ length: columns }).map((_, col) => (
        <div key={col} className="kanban-col">
          <div className="kanban-col-header">
            <Bar width={90} />
          </div>
          {Array.from({ length: 2 + (col % 2) }).map((__, card) => (
            <div key={card} className="kanban-card stack" style={{ gap: 8 }}>
              <Bar width="80%" />
              <Bar width="55%" height={11} />
              <Bar width="40%" height={11} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

/** Skeleton for the application detail page. */
export function DetailSkeleton() {
  return (
    <div className="stack" aria-busy="true" aria-label="Loading">
      <Bar width={240} height={28} />
      <div className="detail-grid">
        <div className="stack">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card">
              <div className="card-body stack">
                <Bar width="40%" />
                <Bar width="90%" height={11} />
                <Bar width="75%" height={11} />
              </div>
            </div>
          ))}
        </div>
        <div className="card">
          <div className="card-body stack">
            <Bar width="50%" />
            {Array.from({ length: 5 }).map((_, i) => (
              <Bar key={i} width="100%" height={11} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
