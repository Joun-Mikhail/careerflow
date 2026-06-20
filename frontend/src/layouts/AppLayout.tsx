import { NavLink, Outlet } from 'react-router-dom';

import {
  BarChartIcon,
  BriefcaseIcon,
  BuildingIcon,
  CheckSquareIcon,
  DashboardIcon,
  LogOutIcon,
  MoonIcon,
  SunIcon,
} from '@/components/icons';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { initials } from '@/lib/format';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: DashboardIcon, end: true },
  { to: '/applications', label: 'Applications', icon: BriefcaseIcon, end: false },
  { to: '/companies', label: 'Companies', icon: BuildingIcon, end: false },
  { to: '/tasks', label: 'Tasks', icon: CheckSquareIcon, end: false },
  { to: '/analytics', label: 'Analytics', icon: BarChartIcon, end: false },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src="/favicon.svg" alt="" className="logo" />
          CareerFlow
        </div>

        <nav className="nav">
          <span className="nav-section">Workspace</span>
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <Icon />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="row" style={{ padding: '0 var(--space-2)' }}>
            <div className="avatar">{initials(user?.full_name ?? null, user?.email ?? '')}</div>
            <div style={{ minWidth: 0 }}>
              <div className="truncate" style={{ color: '#fff', fontWeight: 600, fontSize: '0.85rem' }}>
                {user?.full_name ?? 'Your account'}
              </div>
              <div className="truncate subtle">{user?.email}</div>
            </div>
          </div>
          <button className="nav-item" onClick={logout} style={{ width: '100%' }}>
            <LogOutIcon />
            Sign out
          </button>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <div className="spacer" />
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? <MoonIcon /> : <SunIcon />}
          </button>
        </header>
        <main className="page">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
