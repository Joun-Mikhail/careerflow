import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div className="center-state" style={{ minHeight: '100vh' }}>
      <div className="empty-state">
        <div className="empty-icon" style={{ fontWeight: 800, fontSize: '1.4rem' }}>404</div>
        <h3>Page not found</h3>
        <p className="muted">The page you’re looking for doesn’t exist or has moved.</p>
        <Link to="/" className="btn btn-primary">Back to dashboard</Link>
      </div>
    </div>
  );
}
