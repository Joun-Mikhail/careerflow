import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

import { queryClient } from '@/lib/queryClient';
import type { Token, User } from '@/lib/types';
import { api, setUnauthorizedHandler, tokenStore } from '@/services/api';
import { authApi } from '@/services/auth';
import type { Credentials, RegisterPayload } from '@/services/auth';

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

interface AuthContextValue {
  user: User | null;
  status: AuthStatus;
  login: (credentials: Credentials) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  updateProfile: (fullName: string | null) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<AuthStatus>('loading');

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
    setStatus('unauthenticated');
    queryClient.clear();
  }, []);

  // Restore a session from a stored token on first load.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      setUser(null);
      setStatus('unauthenticated');
    });

    if (!tokenStore.get()) {
      setStatus('unauthenticated');
      return;
    }
    authApi
      .me()
      .then((me) => {
        setUser(me);
        setStatus('authenticated');
      })
      .catch(() => {
        tokenStore.clear();
        setStatus('unauthenticated');
      });
  }, []);

  const applyAuth = useCallback((token: Token, nextUser: User) => {
    tokenStore.set(token.access_token, token.refresh_token);
    api.defaults.headers.common.Authorization = `Bearer ${token.access_token}`;
    setUser(nextUser);
    setStatus('authenticated');
  }, []);

  const login = useCallback(
    async (credentials: Credentials) => {
      const { token, user: nextUser } = await authApi.login(credentials);
      applyAuth(token, nextUser);
    },
    [applyAuth],
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      const { token, user: nextUser } = await authApi.register(payload);
      applyAuth(token, nextUser);
    },
    [applyAuth],
  );

  const updateProfile = useCallback(async (fullName: string | null) => {
    const updated = await authApi.updateProfile(fullName);
    setUser(updated);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, status, login, register, updateProfile, logout }),
    [user, status, login, register, updateProfile, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
