import { Outlet } from 'react-router-dom';

import { CheckSquareIcon } from '@/components/icons';

const HERO_POINTS = [
  'Track every application from wishlist to offer',
  'Never miss an interview or follow-up again',
  'See what is actually working with analytics',
];

export function AuthLayout() {
  return (
    <div className="auth-shell">
      <section className="auth-hero">
        <div className="sidebar-brand" style={{ padding: 0 }}>
          <img src="/favicon.svg" alt="" className="logo" />
          CareerFlow
        </div>
        <h1>Your job search, finally organized.</h1>
        <div className="hero-points">
          {HERO_POINTS.map((point) => (
            <div key={point} className="hero-point">
              <CheckSquareIcon width={20} height={20} />
              <span>{point}</span>
            </div>
          ))}
        </div>
      </section>
      <section className="auth-form-side">
        <Outlet />
      </section>
    </div>
  );
}
