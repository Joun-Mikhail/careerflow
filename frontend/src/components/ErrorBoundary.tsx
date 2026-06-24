import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  message: string | null;
}

/**
 * Top-level error boundary. Catches render-time exceptions anywhere in the
 * tree, reports them (Sentry, when configured), and shows a recoverable
 * fallback instead of a blank white screen.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Hook for monitoring; Sentry's own boundary also captures these.
    console.error('Unhandled UI error:', error, info.componentStack);
  }

  handleReload = (): void => {
    window.location.assign('/');
  };

  render(): ReactNode {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="center-state" style={{ minHeight: '100vh' }}>
        <div className="empty-state">
          <div className="empty-icon" style={{ fontSize: '1.6rem' }}>⚠️</div>
          <h3>Something went wrong</h3>
          <p className="muted">
            An unexpected error interrupted the app. Reloading usually fixes it.
          </p>
          <button className="btn btn-primary" onClick={this.handleReload}>
            Reload app
          </button>
        </div>
      </div>
    );
  }
}
