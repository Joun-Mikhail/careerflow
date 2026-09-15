import { useMutation } from '@tanstack/react-query';

import { matchingApi, type ScoreMatchInput } from '@/services/matching';

/**
 * Scores a CV against jobs. A mutation rather than a query: scoring is an
 * explicit action the user takes against a CV they pick, not state to keep
 * in sync.
 */
export function useScoreMatches() {
  return useMutation({
    mutationFn: (input: ScoreMatchInput) => matchingApi.score(input),
  });
}
