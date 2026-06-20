import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import { tasksApi } from '@/services/tasks';
import type { TaskInput, TaskListParams } from '@/services/tasks';

function invalidateTasks(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: ['tasks'] });
  qc.invalidateQueries({ queryKey: queryKeys.dashboard });
}

export function useTasks(params: TaskListParams = {}) {
  return useQuery({
    queryKey: queryKeys.tasks(params),
    queryFn: () => tasksApi.list(params),
  });
}

export function useCreateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: TaskInput) => tasksApi.create(input),
    onSuccess: () => invalidateTasks(qc),
  });
}

export function useUpdateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      input,
    }: {
      id: string;
      input: Partial<TaskInput> & { is_completed?: boolean };
    }) => tasksApi.update(id, input),
    onSuccess: () => invalidateTasks(qc),
  });
}

export function useToggleTaskComplete() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, completed }: { id: string; completed: boolean }) =>
      completed ? tasksApi.complete(id) : tasksApi.update(id, { is_completed: false }),
    onSuccess: () => invalidateTasks(qc),
  });
}

export function useDeleteTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => tasksApi.remove(id),
    onSuccess: () => invalidateTasks(qc),
  });
}
