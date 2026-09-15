import type { JobMatch, MatchVerdict } from '@/lib/types';

const VERDICT_LABEL: Record<MatchVerdict, string> = {
  strong: 'Strong match',
  promising: 'Promising',
  stretch: 'Stretch',
};

/** The score as a compact, colour-coded badge. */
export function MatchBadge({ match }: { match: JobMatch }) {
  return (
    <span
      className={`badge match-badge match-badge--${match.verdict}`}
      title={VERDICT_LABEL[match.verdict]}
    >
      {match.score}%
    </span>
  );
}

/**
 * Why a job scored what it did. Leads with what is missing, since that is the
 * part a candidate can act on before applying.
 */
export function MatchDetail({ match }: { match: JobMatch }) {
  const { breakdown } = match;
  return (
    <div className="match-detail">
      <p className="match-detail-line">
        <strong>{VERDICT_LABEL[match.verdict]}</strong>{' '}
        <span className="muted">
          — skills {breakdown.skills}% · keywords {breakdown.keywords}% · seniority{' '}
          {breakdown.seniority}%
        </span>
      </p>

      {match.missing_skills.length > 0 && (
        <p className="match-detail-line">
          <span className="match-detail-label">Not in your CV</span>
          {match.missing_skills.map((skill) => (
            <span key={skill} className="chip chip--gap">
              {skill}
            </span>
          ))}
        </p>
      )}

      {match.matched_skills.length > 0 && (
        <p className="match-detail-line">
          <span className="match-detail-label">Covered</span>
          {match.matched_skills.map((skill) => (
            <span key={skill} className="chip chip--ok">
              {skill}
            </span>
          ))}
        </p>
      )}

      {match.missing_skills.length === 0 && match.matched_skills.length === 0 && (
        <p className="muted" style={{ margin: 0 }}>
          This posting names no recognised skills, so the score leans on its wording.
        </p>
      )}
    </div>
  );
}
