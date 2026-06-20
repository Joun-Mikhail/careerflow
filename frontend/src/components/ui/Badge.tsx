import { priorityLabel, statusLabel } from '@/lib/format';
import type { ApplicationStatus, TaskPriority } from '@/lib/types';

export function StatusBadge({ status }: { status: ApplicationStatus }) {
  return <span className={`badge badge--${status}`}>{statusLabel(status)}</span>;
}

export function PriorityBadge({ priority }: { priority: TaskPriority }) {
  return <span className={`badge badge--${priority}`}>{priorityLabel(priority)}</span>;
}
