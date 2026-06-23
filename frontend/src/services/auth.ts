import { api } from './api';

import type { AuthResponse, User } from '@/lib/types';

export interface Credentials {
  email: string;
  password: string;
}

export interface RegisterPayload extends Credentials {
  full_name?: string;
}

export interface PasswordChangePayload {
  current_password: string;
  new_password: string;
}

export const authApi = {
  register: (payload: RegisterPayload) =>
    api.post<AuthResponse>('/auth/register', payload).then((r) => r.data),
  login: (payload: Credentials) =>
    api.post<AuthResponse>('/auth/login', payload).then((r) => r.data),
  me: () => api.get<User>('/auth/me').then((r) => r.data),
  updateProfile: (fullName: string | null) =>
    api.patch<User>('/auth/me', { full_name: fullName }).then((r) => r.data),
  changePassword: (payload: PasswordChangePayload) =>
    api.post<{ message: string }>('/auth/change-password', payload).then((r) => r.data),
};
