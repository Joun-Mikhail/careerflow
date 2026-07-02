import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, useTheme } from './ThemeContext';

function mockMatchMedia(matches: boolean) {
  window.matchMedia = vi.fn().mockImplementation((query: string) => ({
    matches,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
}

function ThemeProbe() {
  const { theme, toggleTheme } = useTheme();
  return <button onClick={toggleTheme}>{theme}</button>;
}

function renderWithProvider() {
  return render(
    <ThemeProvider>
      <ThemeProbe />
    </ThemeProvider>,
  );
}

describe('ThemeContext initial theme', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('falls back to dark when localStorage is empty and OS prefers dark', () => {
    mockMatchMedia(true);
    renderWithProvider();

    expect(screen.getByRole('button')).toHaveTextContent('dark');
    expect(window.matchMedia).toHaveBeenCalledWith('(prefers-color-scheme: dark)');
  });

  it('falls back to light when localStorage is empty and OS prefers light', () => {
    mockMatchMedia(false);
    renderWithProvider();

    expect(screen.getByRole('button')).toHaveTextContent('light');
  });

  it('uses the stored preference over the OS preference', () => {
    localStorage.setItem('careerflow.theme', 'light');
    mockMatchMedia(true); // OS says dark, but stored choice should win
    renderWithProvider();

    expect(screen.getByRole('button')).toHaveTextContent('light');
  });

  it('persists an explicit toggle to localStorage', async () => {
    mockMatchMedia(false);
    renderWithProvider();

    await userEvent.click(screen.getByRole('button'));

    expect(screen.getByRole('button')).toHaveTextContent('dark');
    expect(localStorage.getItem('careerflow.theme')).toBe('dark');
  });
});