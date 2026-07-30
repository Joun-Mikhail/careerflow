import { useState } from 'react';

import { useElapsed } from '@/hooks/useElapsed';
import {
  WAITING_TIPS,
  isSlowWait,
  tipForElapsed,
  waitingMessage,
} from '@/lib/waiting';

/**
 * Full-screen wait used while the session is restored. Shows the current
 * status plus a rotating job-search tip so a cold start reads as a moment of
 * useful downtime rather than a hang.
 */
export function WaitingRoom({ label = 'Loading…' }: { label?: string }) {
  // Vary the opening tip per mount so a repeat visit is not a repeat read.
  const [offset] = useState(() => Math.floor(Math.random() * WAITING_TIPS.length));
  const elapsed = useElapsed(true);
  const tip = tipForElapsed(elapsed, offset);
  const slow = isSlowWait(elapsed);

  return (
    <div className="waiting">
      <div className="waiting-orb" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>

      <p className="waiting-status" role="status" aria-live="polite">
        {waitingMessage(label, elapsed)}
      </p>

      {slow && (
        <div className="waiting-tip" key={tip}>
          <span className="waiting-tip-label">While you wait</span>
          <p>{tip}</p>
        </div>
      )}
    </div>
  );
}

/**
 * Inline counterpart for waits that happen inside a form, where replacing the
 * whole screen would be jarring. Stays out of the way until the wait is long
 * enough to need explaining.
 */
export function WaitingHint({ active, label }: { active: boolean; label: string }) {
  const elapsed = useElapsed(active);
  if (!active || !isSlowWait(elapsed)) return null;

  return (
    <p className="waiting-hint" role="status" aria-live="polite">
      {waitingMessage(label, elapsed)}
    </p>
  );
}
