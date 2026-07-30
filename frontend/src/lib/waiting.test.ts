import { describe, expect, it } from 'vitest';

import {
  TIP_ROTATION_MS,
  WAITING_TIPS,
  isSlowWait,
  tipForElapsed,
  waitingMessage,
} from './waiting';

describe('waitingMessage', () => {
  it('keeps the caller label while the wait is still short', () => {
    expect(waitingMessage('Restoring your session…', 0)).toBe('Restoring your session…');
    expect(waitingMessage('Restoring your session…', 6_999)).toBe('Restoring your session…');
  });

  it('explains the delay once the wait looks like a cold start', () => {
    expect(waitingMessage('Loading…', 7_000)).toMatch(/waking the server/i);
  });

  it('escalates as the wait grows', () => {
    const messages = [7_000, 20_000, 45_000].map((ms) => waitingMessage('Loading…', ms));
    expect(new Set(messages).size).toBe(3);
    expect(messages[2]).toMatch(/reload/i);
  });
});

describe('isSlowWait', () => {
  it('is false before the first phase and true after it', () => {
    expect(isSlowWait(0)).toBe(false);
    expect(isSlowWait(6_999)).toBe(false);
    expect(isSlowWait(7_000)).toBe(true);
  });
});

describe('tipForElapsed', () => {
  it('holds one tip for a full rotation, then advances', () => {
    expect(tipForElapsed(0)).toBe(WAITING_TIPS[0]);
    expect(tipForElapsed(TIP_ROTATION_MS - 1)).toBe(WAITING_TIPS[0]);
    expect(tipForElapsed(TIP_ROTATION_MS)).toBe(WAITING_TIPS[1]);
  });

  it('wraps around rather than running out of tips', () => {
    const full = TIP_ROTATION_MS * WAITING_TIPS.length;
    expect(tipForElapsed(full)).toBe(WAITING_TIPS[0]);
  });

  it('starts from the requested offset', () => {
    expect(tipForElapsed(0, 3)).toBe(WAITING_TIPS[3]);
    expect(tipForElapsed(TIP_ROTATION_MS, 3)).toBe(WAITING_TIPS[4]);
  });
});
