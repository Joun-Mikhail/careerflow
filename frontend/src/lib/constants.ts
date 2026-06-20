/** Domain constants shared by forms, filters, and the board. */

import type { ApplicationStatus, InterviewMode, TaskPriority } from './types';

export const APPLICATION_STATUSES: ApplicationStatus[] = [
  'wishlist',
  'applied',
  'assessment',
  'interview',
  'final_interview',
  'offer',
  'rejected',
  'accepted',
];

/** Statuses shown as columns on the pipeline board, in order. */
export const PIPELINE_STATUSES: ApplicationStatus[] = [
  'wishlist',
  'applied',
  'assessment',
  'interview',
  'final_interview',
  'offer',
  'accepted',
];

export const TASK_PRIORITIES: TaskPriority[] = ['low', 'medium', 'high'];

export const INTERVIEW_MODES: InterviewMode[] = ['phone', 'video', 'onsite'];

export const INTERVIEW_RESULTS = ['pending', 'passed', 'failed', 'cancelled'] as const;

/** Hex colours per status, kept in sync with tokens.css for chart fills. */
export const STATUS_COLORS: Record<ApplicationStatus, string> = {
  wishlist: '#64748b',
  applied: '#0ea5e9',
  assessment: '#8b5cf6',
  interview: '#f59e0b',
  final_interview: '#d97706',
  offer: '#10b981',
  rejected: '#ef4444',
  accepted: '#059669',
};
