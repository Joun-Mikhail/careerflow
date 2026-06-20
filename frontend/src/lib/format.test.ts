import { describe, expect, it } from 'vitest';

import {
  formatBytes,
  formatSalaryRange,
  initials,
  priorityLabel,
  statusLabel,
  titleCase,
} from './format';

describe('titleCase', () => {
  it('splits on underscores and capitalizes each word', () => {
    expect(titleCase('final_interview')).toBe('Final Interview');
    expect(titleCase('offer')).toBe('Offer');
  });
});

describe('statusLabel / priorityLabel', () => {
  it('renders human-friendly labels', () => {
    expect(statusLabel('offer')).toBe('Offer');
    expect(statusLabel('final_interview')).toBe('Final Interview');
    expect(priorityLabel('high')).toBe('High');
  });
});

describe('formatSalaryRange', () => {
  it('returns an em dash when no salary is set', () => {
    expect(formatSalaryRange(null, null, null)).toBe('—');
  });

  it('formats a range with a separator', () => {
    const result = formatSalaryRange(120000, 150000, 'USD');
    expect(result).toContain('–');
    expect(result).toContain('120');
    expect(result).toContain('150');
  });

  it('formats a single bound when only one is provided', () => {
    expect(formatSalaryRange(100000, null, 'USD')).toContain('100');
  });
});

describe('formatBytes', () => {
  it('formats bytes, kilobytes, and megabytes', () => {
    expect(formatBytes(500)).toBe('500 B');
    expect(formatBytes(2048)).toBe('2 KB');
    expect(formatBytes(1572864)).toBe('1.5 MB');
  });
});

describe('initials', () => {
  it('uses the first letters of the full name when available', () => {
    expect(initials('Alex Doe', 'alex@example.com')).toBe('AD');
  });

  it('falls back to the email when no name is set', () => {
    expect(initials(null, 'demo@careerflow.app')).toBe('DE');
  });
});
