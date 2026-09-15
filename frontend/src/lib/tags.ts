import type { InterviewQuestion } from './types';

/** Split a stored comma-separated tag string into individual tags. */
export function parseTags(value: string | null): string[] {
  if (!value) return [];
  return value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean);
}

/**
 * Tags across a set of questions with how often each appears, most used first
 * and alphabetical within a tie so the rail does not reshuffle between renders.
 */
export function tagCounts(questions: InterviewQuestion[]): [string, number][] {
  const counts = new Map<string, number>();
  for (const question of questions) {
    for (const tag of parseTags(question.tags)) {
      counts.set(tag, (counts.get(tag) ?? 0) + 1);
    }
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}
