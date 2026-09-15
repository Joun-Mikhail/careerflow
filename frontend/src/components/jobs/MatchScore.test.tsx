import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { MatchBadge, MatchDetail } from './MatchScore';

import type { JobMatch } from '@/lib/types';

function buildMatch(overrides: Partial<JobMatch> = {}): JobMatch {
  return {
    job_id: 'job-1',
    score: 82,
    verdict: 'strong',
    matched_skills: ['python', 'fastapi'],
    missing_skills: ['kubernetes'],
    missing_keywords: ['payments'],
    breakdown: { skills: 80, keywords: 70, seniority: 100 },
    job_seniority: 'senior',
    cv_seniority: 'senior',
    ...overrides,
  };
}

describe('MatchBadge', () => {
  it('shows the score and labels the verdict', () => {
    render(<MatchBadge match={buildMatch()} />);
    const badge = screen.getByTitle('Strong match');
    expect(badge).toHaveTextContent('82%');
  });

  it('styles each verdict differently', () => {
    const { rerender } = render(<MatchBadge match={buildMatch({ verdict: 'strong' })} />);
    expect(screen.getByTitle('Strong match').className).toContain('match-badge--strong');

    rerender(<MatchBadge match={buildMatch({ verdict: 'stretch' })} />);
    expect(screen.getByTitle('Stretch').className).toContain('match-badge--stretch');
  });
});

describe('MatchDetail', () => {
  it('reports the component scores', () => {
    render(<MatchDetail match={buildMatch()} />);
    expect(screen.getByText(/skills 80%/)).toBeInTheDocument();
    expect(screen.getByText(/keywords 70%/)).toBeInTheDocument();
    expect(screen.getByText(/seniority 100%/)).toBeInTheDocument();
  });

  it('separates what is missing from what is covered', () => {
    render(<MatchDetail match={buildMatch()} />);
    expect(screen.getByText('Not in your CV')).toBeInTheDocument();
    expect(screen.getByText('kubernetes')).toBeInTheDocument();
    expect(screen.getByText('Covered')).toBeInTheDocument();
    expect(screen.getByText('python')).toBeInTheDocument();
  });

  it('omits the missing section when nothing is missing', () => {
    render(<MatchDetail match={buildMatch({ missing_skills: [] })} />);
    expect(screen.queryByText('Not in your CV')).not.toBeInTheDocument();
    expect(screen.getByText('Covered')).toBeInTheDocument();
  });

  it('explains a posting that names no recognised skills', () => {
    render(<MatchDetail match={buildMatch({ matched_skills: [], missing_skills: [] })} />);
    expect(screen.getByText(/names no recognised skills/)).toBeInTheDocument();
  });
});
