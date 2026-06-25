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
import { DocumentsPage } from './pages/DocumentsPage';
import { InterviewsPage } from './pages/InterviewsPage';
import { JobSearchPage } from './pages/JobSearchPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { OffersPage } from './pages/OffersPage';
import { SettingsPage } from './pages/SettingsPage';
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
        <Route path="/interviews" element={<InterviewsPage />} />
        <Route path="/companies" element={<CompaniesPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/job-search" element={<JobSearchPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/offers" element={<OffersPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
