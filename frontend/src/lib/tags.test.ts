import { describe, expect, it } from 'vitest';

import { parseTags, tagCounts } from './tags';

import type { InterviewQuestion } from './types';

function question(tags: string | null): InterviewQuestion {
  return {
    id: crypto.randomUUID(),
    question: 'Q',
    answer: null,
    tags,
    application_id: null,
    asked: false,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };
}

describe('parseTags', () => {
  it('splits a comma-separated string', () => {
    expect(parseTags('behavioural, system design')).toEqual(['behavioural', 'system design']);
  });

  it('treats null and empty as no tags', () => {
    expect(parseTags(null)).toEqual([]);
    expect(parseTags('')).toEqual([]);
  });

  it('drops blanks left by trailing or doubled commas', () => {
    expect(parseTags('sql, , ,')).toEqual(['sql']);
  });
});

describe('tagCounts', () => {
  it('counts how often each tag is used', () => {
    const counts = tagCounts([question('sql'), question('sql, api'), question('api')]);
    expect(counts).toEqual([
      ['api', 2],
      ['sql', 2],
    ]);
  });

  it('orders by use, most used first', () => {
    const counts = tagCounts([question('rare'), question('common'), question('common')]);
    expect(counts[0]).toEqual(['common', 2]);
    expect(counts[1]).toEqual(['rare', 1]);
  });

  it('breaks ties alphabetically so the order is stable', () => {
    const counts = tagCounts([question('zebra'), question('apple')]);
    expect(counts.map(([tag]) => tag)).toEqual(['apple', 'zebra']);
  });

  it('ignores questions with no tags', () => {
    expect(tagCounts([question(null), question('')])).toEqual([]);
  });
});
