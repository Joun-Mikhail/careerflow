import { act, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { WaitingHint, WaitingRoom } from './WaitingRoom';

beforeEach(() => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
});

afterEach(() => {
  vi.useRealTimers();
});

describe('WaitingRoom', () => {
  it('shows the caller label first and no tip yet', () => {
    render(<WaitingRoom label="Restoring your session…" />);
    expect(screen.getByRole('status')).toHaveTextContent('Restoring your session…');
    expect(screen.queryByText('While you wait')).not.toBeInTheDocument();
  });

  it('explains the delay and offers a tip once the wait drags', async () => {
    render(<WaitingRoom label="Restoring your session…" />);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(8_000);
    });

    expect(screen.getByRole('status')).toHaveTextContent(/waking the server/i);
    expect(screen.getByText('While you wait')).toBeInTheDocument();
  });
});

describe('WaitingHint', () => {
  it('renders nothing while inactive', () => {
    const { container } = render(<WaitingHint active={false} label="Signing you in…" />);
    expect(container).toBeEmptyDOMElement();
  });

  it('stays hidden during a fast sign-in', async () => {
    const { container } = render(<WaitingHint active label="Signing you in…" />);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(2_000);
    });
    expect(container).toBeEmptyDOMElement();
  });

  it('appears once the sign-in is slow enough to need explaining', async () => {
    render(<WaitingHint active label="Signing you in…" />);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(8_000);
    });
    expect(screen.getByRole('status')).toHaveTextContent(/waking the server/i);
  });
});
