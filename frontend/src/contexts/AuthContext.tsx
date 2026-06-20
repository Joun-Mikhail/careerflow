import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

import { queryClient } from '@/lib/queryClient';
import type { User } from '@/lib/types';
import { api, setUnauthorizedHandler, tokenStore } from '@/services/api';
import { authApi } from '@/services/auth';
import type { Credentials, RegisterPayload } from '@/services/auth';

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

interface AuthContextValue {
  user: User | null;
  status: AuthStatus;
  login: (credentials: Credentials) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
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

  const applyAuth = useCallback((token: string, nextUser: User) => {
    tokenStore.set(token);
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    setUser(nextUser);
    setStatus('authenticated');
  }, []);

  const login = useCallback(
    async (credentials: Credentials) => {
      const { token, user: nextUser } = await authApi.login(credentials);
      applyAuth(token.access_token, nextUser);
    },
    [applyAuth],
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      const { token, user: nextUser } = await authApi.register(payload);
      applyAuth(token.access_token, nextUser);
    },
    [applyAuth],
  );

  const value = useMemo<AuthContextValue>(
    () => ({ user, status, login, register, logout }),
    [user, status, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
