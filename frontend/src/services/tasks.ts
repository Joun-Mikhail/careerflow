import { api } from './api';

import type { Page, Task, TaskPriority } from '@/lib/types';

export interface TaskInput {
  title: string;
  description?: string | null;
  priority?: TaskPriority;
  due_at?: string | null;
  application_id?: string | null;
}

export interface TaskListParams {
  page?: number;
  page_size?: number;
  is_completed?: boolean;
  priority?: TaskPriority;
  sort?: 'created_at' | 'due_at' | 'priority';
  order?: 'asc' | 'desc';
}

export const tasksApi = {
  list: (params: TaskListParams = {}) =>
    api.get<Page<Task>>('/tasks', { params }).then((r) => r.data),
  create: (input: TaskInput) => api.post<Task>('/tasks', input).then((r) => r.data),
  update: (id: string, input: Partial<TaskInput> & { is_completed?: boolean }) =>
    api.patch<Task>(`/tasks/${id}`, input).then((r) => r.data),
  complete: (id: string) => api.post<Task>(`/tasks/${id}/complete`).then((r) => r.data),
  remove: (id: string) => api.delete(`/tasks/${id}`).then(() => undefined),
};
