import { useState } from 'react';

import { TASK_PRIORITIES } from '@/lib/constants';
import { priorityLabel } from '@/lib/format';
import type { TaskPriority } from '@/lib/types';
import type { TaskInput } from '@/services/tasks';

interface TaskFormProps {
  submitting?: boolean;
  error?: string | null;
  onSubmit: (values: TaskInput) => void;
  onCancel: () => void;
}

export function TaskForm({ submitting, error, onSubmit, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState<TaskPriority>('medium');
  const [dueAt, setDueAt] = useState('');
  const [description, setDescription] = useState('');

  return (
    <form
      className="stack"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          title,
          priority,
          description: description || null,
          due_at: dueAt ? new Date(dueAt).toISOString() : null,
        });
      }}
    >
      {error && <div className="form-error">{error}</div>}
      <div className="field">
        <label className="label">Task</label>
        <input
          className="input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          autoFocus
          placeholder="e.g. Send follow-up email"
        />
      </div>
      <div className="form-row">
        <div className="field">
          <label className="label">Priority</label>
          <select
            className="select"
            value={priority}
            onChange={(e) => setPriority(e.target.value as TaskPriority)}
          >
            {TASK_PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {priorityLabel(p)}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label className="label">Due date</label>
          <input
            className="input"
            type="date"
            value={dueAt}
            onChange={(e) => setDueAt(e.target.value)}
          />
        </div>
      </div>
      <div className="field">
        <label className="label">Details</label>
        <textarea
          className="textarea"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Saving…' : 'Add task'}
        </button>
      </div>
    </form>
  );
}
