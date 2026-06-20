import { useState } from 'react';

import { TaskForm } from '@/components/forms/TaskForm';
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States';
import { CheckSquareIcon, PlusIcon, TrashIcon } from '@/components/icons';
import { PriorityBadge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import {
  useCreateTask,
  useDeleteTask,
  useTasks,
  useToggleTaskComplete,
} from '@/hooks/useTasks';
import { formatDate } from '@/lib/format';
import { ApiError } from '@/services/api';
import type { TaskInput } from '@/services/tasks';

type Filter = 'all' | 'active' | 'completed';

const FILTERS: { key: Filter; label: string; value?: boolean }[] = [
  { key: 'active', label: 'Active', value: false },
  { key: 'completed', label: 'Completed', value: true },
  { key: 'all', label: 'All' },
];

export function TasksPage() {
  const [filter, setFilter] = useState<Filter>('active');
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const selected = FILTERS.find((f) => f.key === filter)!;
  const { data, isLoading, isError, refetch } = useTasks({
    is_completed: selected.value,
    sort: 'due_at',
    order: 'asc',
    page_size: 100,
  });
  const createTask = useCreateTask();
  const toggleComplete = useToggleTaskComplete();
  const deleteTask = useDeleteTask();

  async function handleCreate(values: TaskInput) {
    setFormError(null);
    try {
      await createTask.mutateAsync(values);
      setCreating(false);
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Could not create task.');
    }
  }

  const tasks = data?.items ?? [];

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Tasks</h1>
          <p className="page-subtitle">Follow-ups and prep, prioritized.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setCreating(true)}>
          <PlusIcon /> Add task
        </button>
      </div>

      <div className="toolbar">
        <div className="row" style={{ gap: 4 }}>
          {FILTERS.map((f) => (
            <button
              key={f.key}
              className={`btn btn-sm ${filter === f.key ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilter(f.key)}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        {isLoading ? (
          <LoadingState />
        ) : isError ? (
          <ErrorState error={null} onRetry={refetch} />
        ) : tasks.length === 0 ? (
          <EmptyState
            icon={<CheckSquareIcon />}
            title={filter === 'completed' ? 'No completed tasks yet' : 'Nothing on your list'}
            description="Add a task to keep your follow-ups on track."
            action={
              <button className="btn btn-primary" onClick={() => setCreating(true)}>
                Add task
              </button>
            }
          />
        ) : (
          <ul style={{ listStyle: 'none' }}>
            {tasks.map((task) => (
              <li
                key={task.id}
                className="row-between"
                style={{ padding: 'var(--space-4)', borderBottom: '1px solid var(--border)' }}
              >
                <label className="row" style={{ gap: 'var(--space-3)', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={task.is_completed}
                    onChange={(e) =>
                      toggleComplete.mutate({ id: task.id, completed: e.target.checked })
                    }
                  />
                  <span
                    style={{
                      textDecoration: task.is_completed ? 'line-through' : 'none',
                      color: task.is_completed ? 'var(--text-muted)' : 'var(--text)',
                      fontWeight: 550,
                    }}
                  >
                    {task.title}
                  </span>
                </label>
                <div className="row" style={{ gap: 'var(--space-3)' }}>
                  {task.due_at && <span className="subtle">{formatDate(task.due_at)}</span>}
                  <PriorityBadge priority={task.priority} />
                  <button
                    className="btn-icon btn-ghost"
                    aria-label="Delete task"
                    onClick={() => deleteTask.mutate(task.id)}
                  >
                    <TrashIcon width={16} height={16} />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <Modal open={creating} title="Add task" onClose={() => setCreating(false)}>
        <TaskForm
          submitting={createTask.isPending}
          error={formError}
          onSubmit={handleCreate}
          onCancel={() => setCreating(false)}
        />
      </Modal>
    </>
  );
}
