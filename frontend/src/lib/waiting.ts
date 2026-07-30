/**
 * Copy and timing for long waits (session restore, sign-in).
 *
 * The API is hosted on a plan that suspends idle instances, so the first
 * request after a quiet period can take the better part of a minute. Rather
 * than show a bare spinner for that long, the UI rotates job-search tips and
 * escalates its status message as the wait grows — the message always
 * describes what is actually happening, never a fabricated progress figure.
 */

/** How long each tip stays on screen. */
export const TIP_ROTATION_MS = 4500;

/** Typed as non-empty so indexing can always fall back to the first tip. */
export const WAITING_TIPS: readonly [string, ...string[]] = [
  'Applications sent Tuesday through Thursday tend to get read soonest.',
  'Track every application — the pipeline is easier to work than your memory.',
  'A short, specific follow-up a week later is the cheapest way to stand out.',
  'Name the role and company in your CV filename. Recruiters sort by filename.',
  'Log what you talked about after each interview. Round three will thank you.',
  'Mirror the words in the job posting; many CVs are filtered before a human reads them.',
  'Rejections are data. Note the stage you reached and look for the pattern.',
  'Keep a "wins" file. Interview answers get much easier to write from it.',
  'Ask what success looks like in the first 90 days — the answer is very revealing.',
  'Negotiating is expected. The first number is rarely the final number.',
];

/** Point at which a wait stops looking normal and gets explained. */
export const SLOW_WAIT_MS = 7_000;

interface WaitPhase {
  /** Milliseconds elapsed before this message takes over. */
  readonly after: number;
  readonly message: string;
}

/** Ordered from longest wait to shortest so the first match wins. */
const WAIT_PHASES: readonly WaitPhase[] = [
  {
    after: 45_000,
    message: 'This is slower than usual. If nothing happens shortly, reload the page.',
  },
  {
    after: 20_000,
    message: 'Almost there — idle servers take a moment to spin back up.',
  },
  {
    after: SLOW_WAIT_MS,
    message: 'Waking the server. The first request after a quiet spell is the slow one.',
  },
];

/**
 * The status line to show for a wait of `elapsedMs`, falling back to `base`
 * until the wait is long enough to be worth explaining.
 */
export function waitingMessage(base: string, elapsedMs: number): string {
  return WAIT_PHASES.find((phase) => elapsedMs >= phase.after)?.message ?? base;
}

/** True once the wait has run long enough to deserve an explanation. */
export function isSlowWait(elapsedMs: number): boolean {
  return elapsedMs >= SLOW_WAIT_MS;
}

/**
 * The tip to display, rotating on a fixed cadence. `offset` lets a caller
 * start somewhere other than the first tip so repeat visits vary.
 */
export function tipForElapsed(elapsedMs: number, offset = 0): string {
  const step = Math.floor(elapsedMs / TIP_ROTATION_MS);
  const index = (offset + step) % WAITING_TIPS.length;
  return WAITING_TIPS[index] ?? WAITING_TIPS[0];
}
