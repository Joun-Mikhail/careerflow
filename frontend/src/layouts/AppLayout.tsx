import { useEffect, useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';

import {
  BarChartIcon,
  BriefcaseIcon,
  BuildingIcon,
  CalendarIcon,
  CheckSquareIcon,
  DashboardIcon,
  DollarSignIcon,
  LogOutIcon,
  MenuIcon,
  MoonIcon,
  SettingsIcon,
  SunIcon,
} from '@/components/icons';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { initials } from '@/lib/format';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: DashboardIcon, end: true },
  { to: '/applications', label: 'Applications', icon: BriefcaseIcon, end: false },
  { to: '/interviews', label: 'Interviews', icon: CalendarIcon, end: false },
  { to: '/companies', label: 'Companies', icon: BuildingIcon, end: false },
  { to: '/tasks', label: 'Tasks', icon: CheckSquareIcon, end: false },
  { to: '/offers', label: 'Offers', icon: DollarSignIcon, end: false },
  { to: '/analytics', label: 'Analytics', icon: BarChartIcon, end: false },
  { to: '/settings', label: 'Settings', icon: SettingsIcon, end: false },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [navOpen, setNavOpen] = useState(false);
  const location = useLocation();

  // Close the mobile drawer whenever the route changes.
  useEffect(() => {
    setNavOpen(false);
  }, [location.pathname]);

  // Lock body scroll while the drawer is open on mobile.
  useEffect(() => {
    document.body.style.overflow = navOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [navOpen]);

  return (
    <div className="app-shell">
      {navOpen && <div className="sidebar-backdrop" onClick={() => setNavOpen(false)} />}

      <aside className={`sidebar${navOpen ? ' open' : ''}`}>
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
          <button
            className="icon-btn nav-toggle"
            onClick={() => setNavOpen((v) => !v)}
            aria-label="Open navigation menu"
            aria-expanded={navOpen}
          >
            <MenuIcon />
          </button>
          <div className="topbar-brand">
            <img src="/favicon.svg" alt="" className="logo" width={22} height={22} />
            CareerFlow
          </div>
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
