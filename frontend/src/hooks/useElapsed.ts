import { useEffect, useState } from 'react';

/**
 * Milliseconds since `active` became true, updated on `intervalMs`.
 * Resets to zero whenever the wait ends, so a later wait starts fresh.
 */
export function useElapsed(active: boolean, intervalMs = 500): number {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!active) {
      setElapsed(0);
      return;
    }
    const startedAt = Date.now();
    const id = window.setInterval(() => {
      setElapsed(Date.now() - startedAt);
    }, intervalMs);
    return () => window.clearInterval(id);
  }, [active, intervalMs]);

  return elapsed;
}
