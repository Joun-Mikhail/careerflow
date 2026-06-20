import { Navigate, Route, Routes } from 'react-router-dom';

import { LoadingState } from './components/feedback/States';
import { useAuth } from './contexts/AuthContext';
import { AppLayout } from './layouts/AppLayout';
import { AuthLayout } from './layouts/AuthLayout';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ApplicationDetailPage } from './pages/ApplicationDetailPage';
import { ApplicationsPage } from './pages/ApplicationsPage';
import { CompaniesPage } from './pages/CompaniesPage';
import { DashboardPage } from './pages/DashboardPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { TasksPage } from './pages/TasksPage';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';

function RequireAuth({ children }: { children: JSX.Element }) {
  const { status } = useAuth();
  if (status === 'loading') return <LoadingState label="Restoring your session…" />;
  if (status === 'unauthenticated') return <Navigate to="/login" replace />;
  return children;
}

function PublicOnly({ children }: { children: JSX.Element }) {
  const { status } = useAuth();
  if (status === 'loading') return <LoadingState />;
  if (status === 'authenticated') return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route
        element={
          <PublicOnly>
            <AuthLayout />
          </PublicOnly>
        }
      >
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route path="/" element={<DashboardPage />} />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route path="/applications/:id" element={<ApplicationDetailPage />} />
        <Route path="/companies" element={<CompaniesPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
